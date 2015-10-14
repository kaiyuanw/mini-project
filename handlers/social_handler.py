__author__ = 'Kaiyuan_Wang'

import webapp2

from domain import jinja_env


JINJA_ENVIRONMENT = jinja_env.get_jinja_env()

class SocialPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/social.html')
        self.response.write(template.render())

app = webapp2.WSGIApplication(
    [
        ('/social', SocialPage)
    ],
    debug=True)