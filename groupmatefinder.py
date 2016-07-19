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

# template directory
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))
# obtain list of modules from nusmods api
module_list = json.load(urllib2.urlopen(
    "http://api.nusmods.com/2015-2016/1/moduleList.json"))

# Datastore definitions
class Student(ndb.Model):
    # Sub model for representing a student
    nickname = ndb.StringProperty() # student's nickname
    student_id = ndb.StringProperty() # student matric num
    num_mod = ndb.IntegerProperty() # num of mods student is taking

# id by module code
class Module(ndb.Model):
    code = ndb.StringProperty()
    name = ndb.StringProperty()
    num_students = ndb.IntegerProperty(default=0)
    num_groups = ndb.IntegerProperty(default=0)

    # each module forms one entity
    def save_mod(mod):
        mod_key = mod.put()
        return mod_key

    def get_mod(mod_key):
        mod = mod_key.get()
        return mod

# id by student nickname
class Account(ndb.Model):
    # Model for representing a user's account; the student's profile
    # Key is the user nickname
    student = ndb.StructuredProperty(Student)
    mods_taking = ndb.StructuredProperty(Module, repeated=True)

    def new_account(acc):
        acc_key = acc.put()
        return acc_key

    def get_account(acc_key):
        acc = acc_key.get()
        return acc
    
    def get_mods(self):
        return self.mods_taking


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
            template_values = {
                'user_nickname': users.get_current_user().nickname(),
                'logout': users.create_logout_url(self.request.host_url),
                'email': users.get_current_user(),
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

        """ Note: this code does not set an ID for the new entity,
        without an ID, the datastore generates a unique numeric ID
        when the object is saved for the first time.
        need ID parameter to use an ID generated by this app."""

        if user: # signed in already
            # obtain student account information
            acc_key = ndb.Key('Account', users.get_current_user().nickname())
            stu_acc = acc_key.get()

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
                    new_mod.num_groups = 0
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
            template_values = {
                'user_nickname': users.get_current_user().nickname(),
                'logout': users.create_logout_url(self.request.host_url),
                }
            template = jinja_environment.get_template('profiling_questions.html')
            self.response.out.write(template.render(template_values))
        else:
            template = jinja_environment.get_template('profiling_questions.html')
            self.response.out.write(template.render())

"""    def post(self):
        user = users.get_current_user()

        curr = ndb.Key('Profile', users.get_current_user().nickname())
        profile = curr.get()
#        if user:
        profile.student = Student(
            email = users.get_current_user(),
            nickname = users.get_current_user().nickname())
        # .get("Submit")?
        work_time_ans = self.request.get('work_time')
        profile.work_time = work_time_ans
        profile.put()

        template_values = {
            'user_nickname': users.get_current_user().nickname(),
            'logout': users.create_logout_url(self.request.host_url),
            'work_time': profile.work_time,
            }
        template = jinja_environment.get_template('profiling_questions.html')
        self.response.out.write(template.render(template_values))
"""

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
