# Request handlers for http://groupmatefinder.appspot.com/
# Author: Team Catfish, Orbital


import urllib
import webapp2
import jinja2
import os
import urllib2
import json

# for formatting
from google.appengine.ext import ndb
# user information
from google.appengine.api import users
from google.appengine.api import mail


""" Global Variables """
# template directory
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))
# obtain list of modules from nusmods api
module_list = json.load(urllib2.urlopen(
    "http://api.nusmods.com/2015-2016/1/moduleList.json"))
profiling_qns = {'q1a': 'in the morning', 'q1b': 'in the afternoon',
                 'q1c': 'at night', 'q1d': 'no preference',
                 'q2a': 'meet online', 'q2b': 'meet my groupmate(s) in person',
                 'q2c': 'no preference',
                 'q3a': 'Come on guys! Last Lap! Let\'s go for the best we could be!',
                 'q3b': 'We\'ve done enough, guys. Let\'s go get some rest.',
                 'q4a': 'Let\'s go for it! In the long run what we learn is more important than the grades we get.',
                 'q4b': 'Well, to be realistic, we do need good grades. Let\'s go for something safer.',
                 'q5a': 'the work is done well and efficiently',
                 'q5b': 'everyone\'s feelings are taken care of and friendships are forged among the group'}


""" Datastore definitions """

# Model for representing a student
# id is student_id
class Student(ndb.Model):
    nickname = ndb.StringProperty() # student's name
    student_id = ndb.StringProperty() # for now, student email for identification

# Model that stores information on a particular module
# id by module code
class Module(ndb.Model):
    # Key is the module code
    code = ndb.StringProperty()
    name = ndb.StringProperty()
    num_students = ndb.IntegerProperty(default=0)
# add in when formed!
# groups = ndb.StructuredProperty('Project_Group', repeated=True)

    # each module forms one entity
    def save_mod(mod):
        mod_key = mod.put()
        return mod_key

    def get_mod(mod_key):
        mod = mod_key.get()
        return mod

# Model for the list of answers to the profiling questions
# id is the student nickname
class ProfilingAns(ndb.Model):
    num_answered = ndb.IntegerProperty(default=0)
    # work time preference
    work_pref1 = ndb.StringProperty()
    # way to meet
    work_pref2 = ndb.StringProperty()
    # whether student encourages the team
    work_pref3 = ndb.StringProperty()
    work_pref4 = ndb.StringProperty()
    work_pref5 = ndb.StringProperty()

# Model for representing a user's account; the student's profile
# id by student nickname
class Account(ndb.Model):
    student = ndb.StructuredProperty(Student)
    mods_taking = ndb.StructuredProperty(Module, repeated=True)
    stu_profile = ndb.StructuredProperty(ProfilingAns)

    def new_account(acc):
        acc_key = acc.put()
        return acc_key

    def get_account(acc_key):
        acc = acc_key.get()
        return acc
    
    def get_mods(self):
        return self.mods_taking

# Model for representing a single project group
class Project_Group(ndb.Model):
    group_name = ndb.StringProperty()
    # list of students in a particular group
    students_list = ndb.StructuredProperty(Student, repeated=True)


""" Request Handlers """
# Handler for the front page
class HomePage(webapp2.RequestHandler):
    # Front page for those logged in
    def get(self):
        user = users.get_current_user()
        if user:  # signed in already
            template_values = {
                # pass key-value pairs to template
                'user_nickname': users.get_current_user().nickname(),
                'logout': users.create_logout_url(self.request.host_url),
                }
            template = jinja_environment.get_template('profile_student.html')
            self.response.out.write(template.render(template_values))
        else:
            template = jinja_environment.get_template('homepage.html')
            self.response.out.write(template.render())

# Handler for the About page
class About(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:  # signed in already
            template_values = {
                'user_nickname': users.get_current_user().nickname(),
                'logout': users.create_logout_url(self.request.host_url),
                }
            template = jinja_environment.get_template('profile_student.html')
            self.response.out.write(template.render(template_values))
        else:
            template = jinja_environment.get_template('about.html')
            self.response.out.write(template.render())

# Handler for the profile page
class Profile(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        # user should be signed in to view this page
        if user:
            # obtain student account information
            acc_key = ndb.Key('Account', users.get_current_user().nickname())
            stu_acc = acc_key.get()

            if stu_acc == None:
                template_values = {
                    'user_nickname': users.get_current_user().nickname(),
                    'logout': users.create_logout_url(self.request.host_url),
                    'email': users.get_current_user().email(),
                    }
                template = jinja_environment.get_template('profile_student.html')
                self.response.out.write(template.render(template_values))
            else:
                template_values = {
                    'user_nickname': users.get_current_user().nickname(),
                    'logout': users.create_logout_url(self.request.host_url),
                    'email': users.get_current_user().email(),
                    'mods_taking_list': stu_acc.mods_taking,
                    }
                template = jinja_environment.get_template('profile_student.html')
                self.response.out.write(template.render(template_values))
        else:
            template = jinja_environment.get_template('profile_prof.html')
            self.response.out.write(template.render())

# Handler for the Modules page
class Modules(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        # user should be signed in to view this page
        if user:
            # obtain student account information
            acc_key = ndb.Key('Account', users.get_current_user().nickname())
            stu_acc = acc_key.get()

            if stu_acc == None:
                template_values = {
                    'user_nickname': users.get_current_user().nickname(),
                    'logout': users.create_logout_url(self.request.host_url),
                    }
                template = jinja_environment.get_template('modules_student.html')
                self.response.out.write(template.render(template_values))
            else:
                template_values = {
                    'user_nickname': users.get_current_user().nickname(),
                    'logout': users.create_logout_url(self.request.host_url),
                    'mods_taking_list': stu_acc.mods_taking,
                    }
                template = jinja_environment.get_template('modules_student.html')
                self.response.out.write(template.render(template_values))
        else:
            template = jinja_environment.get_template('modules_prof.html')
            self.response.out.write(template.render())

# Handler for the Add Modules page
class Add_Module(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        # user should be signed in to view this page

        if user: # signed in already
            # obtain student account information
            """ Note: this code does not set an ID for the new entity,
            without an ID, the datastore generates a unique numeric ID
            when the object is saved for the first time.
            need ID parameter to use an ID generated by this app."""

            template_values = {
                'user_nickname': users.get_current_user().nickname(),
                'logout': users.create_logout_url(self.request.host_url),
                }
            template = jinja_environment.get_template('add_module.html')
            self.response.out.write(template.render(template_values))
        else:
            template = jinja_environment.get_template('add_module.html')
            self.response.out.write(template.render())

    # Pre-cond: student has not added the mod to list of mods he/she is taking
    def post(self):
        # user should be signed in to view this page

        acc_key = ndb.Key('Account', users.get_current_user().nickname())
        stu_acc = acc_key.get()

        if stu_acc == None:
            stu_acc = Account(id=users.get_current_user().nickname())
            stu_acc.put()

        # self.request.get('<input name>')
        search_id = self.request.get('search_mod')

        # create new mod entity if not already created
        new_mod_key = ndb.Key('Module', search_id)
        new_mod = new_mod_key.get()
        if new_mod == None: # entity for this mod not created before
            new_mod = Module(id = search_id)
            new_mod.code = search_id
            # update relevant information to the entity
            for code in module_list:
                if new_mod.code == code:
                    new_mod.name = module_list[code]
                    new_mod.num_students = 1
                    break
        else: # this mod entity already exists
            curr_stu = new_mod.num_students
            new_mod.num_students = curr_stu + 1
        new_mod.put()

        stu_acc.mods_taking.append(new_mod)
        stu_acc.put() # update student account

        template_values = {
            'user_nickname': users.get_current_user().nickname(),
            'logout': users.create_logout_url(self.request.host_url),
            'new_mod': new_mod,
            'mod_taking': stu_acc.mods_taking,
            }
        self.redirect('/modules')

# Handler for the Profiling Questions page
class Profiling_Questions(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        # user should be signed in to view this page
        if user:
            # obtain profiling qns answers
            curr_ans = ndb.Key('ProfilingAns', users.get_current_user().nickname())
            profiling_ans = curr_ans.get()

            if profiling_ans == None:
                profiling_ans = ProfilingAns(id=users.get_current_user().nickname())

#            profiling_ans.num_answered = 0 # for testing
            profiling_ans.put()

            template_values = {
                'user_nickname': users.get_current_user().nickname(),
                'num_answered': profiling_ans.num_answered,
                'q1a': profiling_qns['q1a'],
                'q1b': profiling_qns['q1b'],
                'q1c': profiling_qns['q1c'],
                'q1d': profiling_qns['q1d'],
                'q2a': profiling_qns['q2a'],
                'q2b': profiling_qns['q2b'],
                'q2c': profiling_qns['q2c'],
                'q3a': profiling_qns['q3a'],
                'q3b': profiling_qns['q3b'],
                'q4a': profiling_qns['q4a'],
                'q4b': profiling_qns['q4b'],
                'q5a': profiling_qns['q5a'],
                'q5b': profiling_qns['q5b'],
                'work_pref1': profiling_ans.work_pref1,
                'work_pref2': profiling_ans.work_pref2,
                'work_pref3': profiling_ans.work_pref3,
                'work_pref4': profiling_ans.work_pref4,
                'work_pref5': profiling_ans.work_pref5,
                'logout': users.create_logout_url(self.request.host_url),
                }
            template = jinja_environment.get_template('profiling_questions.html')
            self.response.out.write(template.render(template_values))
        else:
            template = jinja_environment.get_template('profiling_questions.html')
            self.response.out.write(template.render())

    def post(self):
        user = users.get_current_user()

        if user:
            # obtain student account
            curr = ndb.Key('Account', users.get_current_user().nickname())
            stu_acc = curr.get()

            if stu_acc == None:
                stu_acc = Account(id=users.get_current_user().nickname())

            if stu_acc.student == None:
                stu_acc.student = Student(
                    nickname = users.get_current_user().nickname(),
                    student_id = users.get_current_user().email())

            # obtain profiling qns answers
            curr_ans = ndb.Key('ProfilingAns', users.get_current_user().nickname())
            profiling_ans = curr_ans.get()

            if profiling_ans == None:
                profiling_ans = ProfilingAns(id=users.get_current_user().nickname())


            if profiling_ans.num_answered == 0:
                work_pref1_ans = self.request.get('work_pref1')
                profiling_ans.work_pref1 = work_pref1_ans
                profiling_ans.num_answered += 1
            elif profiling_ans.num_answered == 1:
                work_pref2_ans = self.request.get('work_pref2')
                profiling_ans.work_pref2 = work_pref2_ans
                profiling_ans.num_answered += 1
            elif profiling_ans.num_answered == 2:
                work_pref3_ans = self.request.get('work_pref3')
                profiling_ans.work_pref3 = work_pref3_ans
                profiling_ans.num_answered += 1
            elif profiling_ans.num_answered == 3:
                work_pref4_ans = self.request.get('work_pref4')
                profiling_ans.work_pref4 = work_pref4_ans
                profiling_ans.num_answered += 1
            elif profiling_ans.num_answered == 4:
                work_pref5_ans = self.request.get('work_pref5')
                profiling_ans.work_pref5 = work_pref5_ans
                profiling_ans.num_answered += 1

            profiling_ans.put()
            stu_acc.put()

            template_values = {
                'user_nickname': users.get_current_user().nickname(),
                'logout': users.create_logout_url(self.request.host_url),
                'num_answered': profiling_ans.num_answered,
                'q1a': profiling_qns['q1a'],
                'q1b': profiling_qns['q1b'],
                'q1c': profiling_qns['q1c'],
                'q1d': profiling_qns['q1d'],
                'q2a': profiling_qns['q2a'],
                'q2b': profiling_qns['q2b'],
                'q2c': profiling_qns['q2c'],
                'q3a': profiling_qns['q3a'],
                'q3b': profiling_qns['q3b'],
                'q4a': profiling_qns['q4a'],
                'q4b': profiling_qns['q4b'],
                'q5a': profiling_qns['q5a'],
                'q5b': profiling_qns['q5b'],
                'work_pref1': profiling_ans.work_pref1,
                'work_pref2': profiling_ans.work_pref2,
                'work_pref3': profiling_ans.work_pref3,
                'work_pref4': profiling_ans.work_pref4,
                'work_pref5': profiling_ans.work_pref5,
                'logout': users.create_logout_url(self.request.host_url),
                }
            self.redirect('/profilingquestions')
        else:
            template = jinja_environment.get_template('profiling_questions.html')
            self.response.out.write(template.render())

# Handler for the Groups page
class Groups(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        # user should be signed in to view this page
        if user:
            template_values = {
                'user_nickname': users.get_current_user().nickname(),
                'logout': users.create_logout_url(self.request.host_url),
                }
            template = jinja_environment.get_template('groups_student.html')
            self.response.out.write(template.render(template_values))
        else:
            template = jinja_environment.get_template('groups_prof.html')
            self.response.out.write(template.render())
            
app = webapp2.WSGIApplication([('/', HomePage),
                               ('/groupmatefinder', HomePage),
                               ('/about', About),
                               ('/profile', Profile),
                               ('/modules', Modules),
                               ('/addmod', Add_Module),
                               ('/profilingquestions', Profiling_Questions),
                               ('/groups', Groups)],
                              debug=False)
