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
# list of options for profiling questions
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
# num of profiling questions
num_profiling_qns = 5


""" Datastore definitions """

# Model for representing a student
# id is nickname
class Student(ndb.Model):
    nickname = ndb.StringProperty() # student's name
    student_id = ndb.StringProperty() # for now, student email for identification
    is_grouped = ndb.BooleanProperty(default=False)

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
    # reaction to an idea
    work_pref4 = ndb.StringProperty()
    # attitude
    work_pref5 = ndb.StringProperty()

# Model for representing a single project group
# id is the group_name
class Project_Group(ndb.Model):
    group_name = ndb.StringProperty()
    # list of students in a particular group
    student1 = ndb.StructuredProperty(Student)
    student2 = ndb.StructuredProperty(Student)

# Model that stores lists related to a particular module
# Comes in a pair with Module entity;
# necessary due to limitations of ndb that only allows one layer of repeated properties
# id is module code
class Lists_In_Module(ndb.Model):
    stu_list = ndb.StructuredProperty(Student, repeated=True)
    groups = ndb.StructuredProperty(Project_Group, repeated=True)

# Model that stores information on a particular module
# each module forms one entity
# id is module code
class Module(ndb.Model):
    # Key is the module code
    code = ndb.StringProperty()
    name = ndb.StringProperty()

# Model for representing a user's account; the student's profile
# id by student nickname
class Account(ndb.Model):
    student = ndb.StructuredProperty(Student)
    mods_taking = ndb.StructuredProperty(Module, repeated=True)
    stu_profile = ndb.StructuredProperty(ProfilingAns)


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
                    'module_list': module_list,
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
                curr_profile_key = ndb.Key('ProfilingAns', users.get_current_user().nickname())
                curr_profile = curr_profile_key.get()
                if curr_profile == None:
                    curr_profile = ProfilingAns(id=users.get_current_user().nickname())
                    curr_profile.put()
                stu_acc.stu_profile = curr_profile
                stu_acc.put()

                template_values = {
                    'user_nickname': users.get_current_user().nickname(),
                    'logout': users.create_logout_url(self.request.host_url),
                    'mods_taking_list': stu_acc.mods_taking,
                    'num_answered': curr_profile.num_answered,
                    'num_profiling_qns': num_profiling_qns,
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

        # get Student entity
        stu_key = ndb.Key('Student', users.get_current_user().nickname())
        stu = stu_key.get()
        if stu == None:
            stu = Student(id=users.get_current_user().nickname())
        stu.put()

        # create new mod entity and lists entity if not already created
        new_mod_key = ndb.Key('Module', search_id)
        new_mod = new_mod_key.get()

        new_lists_key = ndb.Key('Lists_In_Module', search_id)
        new_lists_mod = new_lists_key.get()

        if new_mod == None: # entity for this mod not created before
            new_mod = Module(id = search_id)
            new_mod.code = search_id

            # update relevant information to the entity
            for code in module_list:
                if new_mod.code == code:
                    new_mod.name = module_list[code]
                    break
        new_mod.put()

        if new_lists_mod == None: # lists entity for this mod not created before
            new_lists_mod = Lists_In_Module(id = search_id)
            new_lists_mod.stu_list.append(stu)

        else: # this mod entity already exists
            new_lists_mod.stu_list.append(stu)
        new_lists_mod.put()

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

            percent_answered = int(profiling_ans.num_answered / float(num_profiling_qns) * 100)

            template_values = {
                'user_nickname': users.get_current_user().nickname(),
                'num_profiling_qns': num_profiling_qns,
                'num_answered': profiling_ans.num_answered,
                'percent_answered': percent_answered,
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

# Match students to form groups. Called through CRON job, runs every 5 mins through the day.
# Currently only able to group pairs
class Match_Groupmates(webapp2.RequestHandler):
    def get(self):
        # algorithm for grouping students!

        for code in module_list:
            # get mod entity if it exists
            curr_mod_key = ndb.Key('Module', code)
            curr_mod = curr_mod_key.get()
            if curr_mod == None: # module entity does not exist
                continue

            # get lists information on particular module
            curr_list_key = ndb.Key('Lists_In_Module', code)
            curr_list_mod = curr_list_key.get()
            if curr_list_mod == None: # lists information for this mod does not exist
                continue

            # obtain list of students taking module
            curr_stu_list = curr_list_mod.stu_list

            # reset is_grouped attribute for all students
            for student in curr_stu_list:
                student.is_grouped = False

            # too few students to form a group, continue
            if len(curr_stu_list) == 0 or len(curr_stu_list) == 1:
                continue
            else:
                iteration = 1
                while len(curr_stu_list) > 0:
                    # compare answers to profiling questions
                    for index1 in range(len(curr_stu_list)):
                        stu1 = curr_stu_list[index1]
                        stu1_ans_key = ndb.Key('ProfilingAns', stu1.nickname)
                        stu1_ans = stu1_ans_key.get()
                        # student is grouped already, go to next student
                        if stu1.is_grouped == True:
                            continue

                        for index2 in range(index1+1, len(curr_stu_list)):
                            stu2 = curr_stu_list[index2]
                            stu2_ans_key = ndb.Key('ProfilingAns', stu2.nickname)
                            stu2_ans = stu2_ans_key.get()
                            # student is grouped already
                            if stu2.is_grouped == True:
                                continue

                            # compare answers
                            num_equal = 0
                            for ans1, ans2 in zip(stu1_ans, stu2_ans):
                                # student needs to answer all questions before being grouped
                                if ans1 == None or ans2 == None:
                                    continue
                                if ans1 == ans2:
                                    num_equal += 1

                            # all answers compared
                            # groups students with 5 answers same together in iter1,
                            # then 4 in iter2, then 3 in iter3...
                            if num_equal == num_profiling_qns - iteration + 1:
                                num_groups = len(curr_list_mod.groups)
                                group_x = Project_Group(group_name = 'group' + num_groups)
                                group_x.student1 = stu1
                                group_x.student1 = stu2
                                group_x.put()
                                curr_list_mod.groups.append(group_x)
                                curr_list_mod.put()
                                stu1.is_grouped = True
                                stu2.is_grouped = True
                                # continues to group the next stu1
                                continue

                    # remove students from list if already grouped, then group the remainder
                    for student in curr_stu_list:
                        if student.is_grouped == True:
                            curr_stu_list.remove(student)
                    iteration += 1

# Handler for the Groups page
class Groups(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        # variables for storing values later
        name_of_group = None
        other_stu = None

        # user should be signed in to view this page
        if user:
            acc_key = ndb.Key('Account', users.get_current_user().nickname())
            stu_acc = acc_key.get()

            if stu_acc:
                # obtain lists of modules student is taking
                # then get information on groups the student is in
                mods_taking_list = stu_acc.mods_taking

                for mod in mods_taking_list:
                    # if not taking any mods yet, cannot show any group
                    if mod.code == None:
                        break

                    module_code = mod.code
                    lists_mod_key = ndb.Key('Lists_In_Module', module_code)
                    lists_mod = lists_mod_key.get()

                    # if lists entity not created before, cannot group any student yet
                    if lists_mod == None: # lists entity for this mod not created before
                        lists_mod = Lists_In_Module(id=module_code)
                        lists_mod.put()
                        break
                    else: # this mod entity already exists
                        # obtain list of groups in the particular module
                        groups_in_mod = lists_mod.groups

                        if groups_in_mod == None:
                            break
                        # find the group that the student is in
                        for group in groups_in_mod:
                            if group == None:
                                break
                            stu1 = group.student1
                            stu2 = group.student2
                            if stu1.nickname == users.get_current_user().nickname():
                                name_of_group = group.group_name
                                other_stu = stu2.nickname
                            elif stu2.nickname == users.get_current_user().nickname():
                                name_of_group = group.group_name
                                other_stu = stu1.nickname

            else:
                stu_acc = Account(id=users.get_current_user().nickname())
                stu_acc.put()

            template_values = {
                'user_nickname': users.get_current_user().nickname(),
                'logout': users.create_logout_url(self.request.host_url),
                'stu_acc': stu_acc,
                'first_mod': stu_acc.mods_taking[0],
                'mods_taking_list': stu_acc.mods_taking,
                'group_name': name_of_group,
                'other_stu': other_stu,
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
                               ('/matchgroupmates', Match_Groupmates),
                               ('/groups', Groups)],
                              debug=False)
