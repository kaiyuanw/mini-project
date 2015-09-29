import os
from google.appengine.api import users
import jinja2
import webapp2

from domain import jinja_env

JINJA_ENVIRONMENT = jinja_env.get_jinja_env()

class LoginPage(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            self.redirect('manage')
        else:
            url = users.create_login_url(self.request.url)
            url_txt = 'Login'
            template_values = {
                'url': url,
                'url_txt': url_txt
            }
            template = JINJA_ENVIRONMENT.get_template('templates/login.html')
            self.response.write(template.render(template_values))


app = webapp2.WSGIApplication([('/', LoginPage)], debug=True)