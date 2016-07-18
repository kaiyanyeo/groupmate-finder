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


# Datastore definitions
class Student(ndb.Model):
    # Sub model for representing a student
#    email = ndb.StringProperty() # student email
    nickname = ndb.StringProperty() # student's nickname
    student_id = ndb.StringProperty() # student matric num
    num_mod = ndb.IntegerProperty() # num of mods student is taking

class Profile(ndb.Model):
    # Model for representing a user's profile
    student = ndb.StructuredProperty(Student)
    work_time = ndb.StringProperty()

class Module(ndb.Model):
    module_list = ndb.JsonProperty()
    module_code = ndb.StringProperty()
    module_name = ndb.StringProperty()
    num_students = ndb.IntegerProperty()
    num_groups = ndb.IntegerProperty()


# This is for the front page
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

# This is the About page
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

# This is for the profile page
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

class Modules(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        # user should be signed in to view this page
        if user:
            template_values = {
                'user_nickname': users.get_current_user().nickname(),
                'logout': users.create_logout_url(self.request.host_url),
                }
            template = jinja_environment.get_template('modules_student.html')
            self.response.out.write(template.render(template_values))
        else:
            template = jinja_environment.get_template('modules_prof.html')
            self.response.out.write(template.render())

class Add_Module(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        # user should be signed in to view this page
        # obtain list of modules from nusmods api
        mod_list = urllib2.urlopen(
            "http://api.nusmods.com/2015-2016/1/moduleList.json")
        modules = Module(
            module_list = json.load(mod_list)
            )

        if user:
            template_values = {
                'user_nickname': users.get_current_user().nickname(),
                'logout': users.create_logout_url(self.request.host_url),
                'mod_list': modules.module_list,
#                'mod_code': modules.module_code,
#                'mod_name': modules.module_name,
                }
            template = jinja_environment.get_template('add_module.html')
            self.response.out.write(template.render(template_values))
        else:
            template = jinja_environment.get_template('add_module.html')
            self.response.out.write(template.render())

    def post(self):
        user = users.get_current_user()
        # user should be signed in to view this page
        # obtain list of modules from nusmods api
        mod_list = urllib2.urlopen(
            "http://api.nusmods.com/2015-2016/1/moduleList.json")
        modules = Module(
            module_list = json.load(mod_list)
            )
        search = self.request.get('search_mod')
        modules.module_code = search

        if user:
            template_values = {
                'user_nickname': users.get_current_user().nickname(),
                'logout': users.create_logout_url(self.request.host_url),
                'mod_list': modules.module_list,
                'mod_code': modules.module_code,
                }
            template = jinja_environment.get_template('add_module.html')
            self.response.out.write(template.render(template_values))


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
