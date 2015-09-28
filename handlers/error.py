__author__ = 'Kaiyuan_Wang'

import webapp2
import jinja_env

JINJA_ENVIRONMENT = jinja_env.get_jinja_env()

class ErrorPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/error.html')
        self.response.write(template.render())

app = webapp2.WSGIApplication(
    [
        ('/error.*', ErrorPage)
    ],
    debug=True)