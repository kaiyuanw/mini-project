__author__ = 'Kaiyuan_Wang'

import webapp2

from domain import jinja_env


JINJA_ENVIRONMENT = jinja_env.get_jinja_env()

class ErrorPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/error.html')
        self.response.write(template.render())

class PageNotFound(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/page_not_found.html')
        self.response.write(template.render())

app = webapp2.WSGIApplication(
    [
        ('/error.*', ErrorPage),
        ('/page_not_found', PageNotFound),
        ('/.*', PageNotFound)
    ],
    debug=True)