import os
from google.appengine.api import users
import jinja2
import webapp2

from domain import jinja_env
from domain.model import MailingList
from domain.key_pool import mailing_list_key

JINJA_ENVIRONMENT = jinja_env.get_jinja_env()

class LoginPage(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            mailing_list = MailingList.query(ancestor = mailing_list_key('mailing_list')).fetch()
            if len(mailing_list) < 1:
                new_mailing_list = MailingList(parent = mailing_list_key('mailing_list'))
                new_mailing_list.report_subscribers = [ users.get_current_user().email() ]
                new_mailing_list.put()
            else:
                mailing_list = mailing_list[0]
                if users.get_current_user().email() not in mailing_list.report_subscribers:
                    mailing_list.report_subscribers.append(users.get_current_user().email())
                    mailing_list.put()
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