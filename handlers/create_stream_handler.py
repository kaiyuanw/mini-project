__author__ = 'Kaiyuan_Wang'

import urllib
import json

from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.api import search
import webapp2

from domain import jinja_env, time
from domain.model import Stream
from domain.key_pool import user_key
from domain.index_pool import stream_index
from domain.suggestions import generate_suggestions

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
            stream_cover_url = 'assets/images/default_cover_img.png'

        streams = Stream.query(Stream.name == stream_name).fetch()
        if len(streams) < 1:
            new_stream = Stream(parent = user_key(users.get_current_user().nickname()))
            new_stream.name = stream_name
            new_stream.cover_url = stream_cover_url
            new_stream.owner = users.get_current_user()
            new_stream.owner_nickname = users.get_current_user().nickname()
            new_stream.create_time = time.get_current_us_central_time()# datetime.datetime.now()
            new_stream.update_time = time.get_current_us_central_time()# datetime.datetime.now()
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
            doc = search.Document(
                fields=[
                    search.TextField(name='stream_name', value=new_stream.name),
                    search.TextField(name='suggestions', value=generate_suggestions(new_stream.name))
                ]
            )
            try:
                index = search.Index(name = stream_index(users.get_current_user().nickname()))
                index.put(doc)
                print index
            except search.Error as e:
                print e.message
            result = { "successful" : "200" }
            self.response.headers['Content-Type'] = 'application/json'
            result = json.dumps(result)
            self.response.write(result)
        else:
            result = { "error" : "A stream of that name already exists! Please select another name." }
            self.response.headers['Content-Type'] = 'application/json'
            result = json.dumps(result)
            self.response.write(result)

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