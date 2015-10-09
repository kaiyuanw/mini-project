__author__ = 'Kaiyuan_Wang'

import webapp2
from google.appengine.api import users

from domain import jinja_env
from domain.model import Stream


JINJA_ENVIRONMENT = jinja_env.get_jinja_env()

class ViewAllStreamsPage(webapp2.RequestHandler):
    def get(self):
        streams = Stream.query().order(-Stream.create_time).fetch()
        template_value = {
            'streams': streams
        }
        template = JINJA_ENVIRONMENT.get_template('templates/view_all_streams.html')
        self.response.out.write(template.render(template_value))

app = webapp2.WSGIApplication(
    [
        ('/view_all_stream', ViewAllStreamsPage)
    ], debug = True)