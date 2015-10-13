__author__ = 'Kaiyuan_Wang'

import urllib

from google.appengine.api import users
from google.appengine.api import mail
import webapp2

from domain import jinja_env, time
from domain.model import Stream
from domain.key_pool import user_key


JINJA_ENVIRONMENT = jinja_env.get_jinja_env()

class CreateStreamPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/create_stream.html')
        self.response.out.write(template.render())

class CreateStream(webapp2.RequestHandler):
    def post(self):
        stream_name = self.request.get('stream_name')
        if len(stream_name) == 0:
            stream_name = 'untitled stream'
        stream_tags = self.request.get('stream_tags').replace('\n', '').split(',')
        stream_subscribers = self.filter_subscriber(self.request.get('subscribers').replace('\n', '').split(','))
        stream_cover_url = self.request.get('cover_url')
        if len(stream_cover_url) == 0:
            stream_cover_url = 'assets/images/default_cover_img.jpg'

        streams = Stream.query(Stream.name == stream_name, Stream.owner == users.get_current_user()).fetch()
        if len(streams) < 1:
            new_stream = Stream(parent = user_key(users.get_current_user().nickname()))
            new_stream.name = stream_name
            new_stream.cover_url = stream_cover_url
            new_stream.owner = users.get_current_user()
            new_stream.owner_nickname = users.get_current_user().nickname()
            new_stream.create_time = time.get_current_us_central_time()# datetime.datetime.now()
            new_stream.update_time = time.get_current_us_central_time()# datetime.datetime.now()
            new_stream.unique_id_counter = 0
            new_stream.pic_num = 0
            new_stream.total_views = 0
            new_stream.total_visits = []
            new_stream.stream_url = urllib.urlencode({'stream_name' : new_stream.name})
            new_stream.guest_url = urllib.urlencode({'show_more' : new_stream.name + '==' + users.get_current_user().nickname()})

            if len(stream_tags) > 0:
                new_stream.tags = stream_tags


            if self.contains_subscriber(stream_subscribers):
                new_stream.subscribers = stream_subscribers
                email_sender = users.get_current_user().email()
                email_subject = 'Stream invitation by user ' + users.get_current_user().nickname()
                msg_prefix = 'You are invited to checkout ' + users.get_current_user().nickname() + '\'s new stream ' + new_stream.name + '\n'
                msg_body = self.request.get('optional_msg')
                for email_receiver in new_stream.subscribers:
                    mail.send_mail(
                        sender = email_sender,
                        to = email_receiver,
                        subject = email_subject,
                        body = msg_prefix + msg_body
                    )
            new_stream.put()
            self.redirect('manage')
        else:
            self.redirect('error')

    def filter_subscriber(self, subscribers):
        for subscriber in subscribers:
            if subscriber == '' or subscriber == users.get_current_user().email():
                subscribers.remove(subscriber)
        return subscribers

    def contains_subscriber(self, subscribers):
        for subscriber in subscribers:
            if len(subscriber) > 0:
                return True
        return False


app = webapp2.WSGIApplication(
    [
        ('/create', CreateStream),
        ('/create_stream', CreateStreamPage)
    ],
    debug=True)