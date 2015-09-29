__author__ = 'Kaiyuan_Wang'

from google.appengine.api import users
import webapp2

import jinja_env
from model import Stream
from key_pool import user_key

JINJA_ENVIRONMENT = jinja_env.get_jinja_env()

class ManagePage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/manage.html')
        if users.get_current_user():
            url_link = users.create_logout_url(self.request.uri)
            url_txt = 'Logout'
            own_streams = Stream.query(
                ancestor = user_key(users.get_current_user().nickname())
            ).order(-Stream.create_time).fetch()

            subscribed_streams = Stream.query(
                Stream.subscribers == users.get_current_user().nickname()
            ).fetch()
            template_value = {
                'own_streams': own_streams,
                'subscribed_streams': subscribed_streams,
                'url_link': url_link,
                'url_txt': url_txt
            }
            self.response.out.write(template.render(template_value))
        else:
            url_link = users.create_login_url(self.request.uri)
            url_txt = 'Login'
            template_value = {
                'own_streams': [],
                'subscribed_streams': [],
                'url_link': url_link,
                'url_txt': url_txt
            }
            self.response.out.write(template.render(template_value))
            self.redirect('/')

app = webapp2.WSGIApplication([('/manage', ManagePage)], debug=True)