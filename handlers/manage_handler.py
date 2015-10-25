__author__ = 'Kaiyuan_Wang'

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import search
import webapp2

from domain import jinja_env
from domain.model import Stream
from domain.model import Photo
from domain.key_pool import user_key
from domain.key_pool import stream_key
from domain.index_pool import stream_index

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

class DeleteStreams(webapp2.RequestHandler):
    def post(self):
        original_url = self.request.headers['Referer']
        streams2delete = self.request.get_all('streams2delete')
        if len(streams2delete) > 0:
            streams = Stream.query(Stream.name.IN(streams2delete), Stream.owner == users.get_current_user()).fetch()
            for stream in streams:
                photos = Photo.query(ancestor = stream_key(stream.name))
                ndb.delete_multi([p.key for p in photos])
            ndb.delete_multi([s.key for s in streams])
            try:
                index = search.Index(name=stream_index(users.get_current_user().nickname()))
                index2delete = []
                for stream_name in streams2delete:
                    for scored_document in index.search('stream_name:\"' + stream_name + '\"'):
                        index2delete.append(scored_document.doc_id)
                if len(index2delete) > 0:
                    index.delete(index2delete)
            except search.Error as e:
                print e.message
        self.redirect(original_url)

class UnsubscribeStreams(webapp2.RequestHandler):
    def post(self):
        original_url = self.request.headers['Referer']
        streams2unsubscribe = self.request.get_all('streams2unsubscribe')
        if len(streams2unsubscribe) > 0:
            streams = Stream.query(Stream.name.IN(streams2unsubscribe)).fetch()
            for stream in streams:
                if users.get_current_user() and users.get_current_user().email() in stream.subscribers:
                    stream.subscribers.remove(users.get_current_user().email())
                    stream.put()
        self.redirect(original_url)

app = webapp2.WSGIApplication(
    [
        ('/manage', ManagePage),
        ('/delete_streams', DeleteStreams),
        ('/unsubscribe_streams', UnsubscribeStreams)
    ], debug=True)