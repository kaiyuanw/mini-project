__author__ = 'Kaiyuan_Wang'

import webapp2
import re
import urllib
import datetime

from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext import ndb

from model import Stream
from model import Photo
from model import SingleVisit
import jinja_env
from key_pool import stream_key

JINJA_ENVIRONMENT = jinja_env.get_jinja_env()


class ViewSingleStreamPage(webapp2.RequestHandler):
    def get(self):
        stream_name = re.findall('%3D(.*)', self.request.url)[0]
        stream = Stream.query(Stream.name == stream_name, Stream.owner == users.get_current_user()).fetch()[0]
        photos = Photo.query(ancestor = stream_key(stream_name)).order(-Photo.upload_date).fetch(3)
        more_pic_url = urllib.urlencode({'show_more': stream.name + '==' + users.get_current_user().nickname()})
        template_value = {
            'stream_name': stream_name,
            'photos': photos,
            'more_pic_url': more_pic_url
        }
        template = JINJA_ENVIRONMENT.get_template('templates/view_single_stream.html')
        self.response.out.write(template.render(template_value))


class Image(webapp2.RequestHandler):
    def get(self):
        photo_key = ndb.Key(urlsafe=self.request.get('img_id'))
        photo = photo_key.get()
        if photo.image:
            # self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(photo.image)
        else:
            self.response.out.write('No image')


class Upload(webapp2.RequestHandler):
    def post(self):
        original_url = self.request.headers['Referer']
        img = self.request.get('photo')
        if len(img) > 0:
            stream_name = re.findall('=(.*)', original_url)[0]
            stream = Stream.query(Stream.name == stream_name, Stream.owner == users.get_current_user()).fetch()[0]
            photo = Photo(parent = stream_key(stream_name))
            stream.update_time = photo.upload_date
            stream.pic_num = stream.pic_num + 1
            stream.unique_id_counter += 1
            photo.id = str(stream.unique_id_counter)
            img = images.resize(img, 300, 300)
            photo.image = img
            photo.put()
            stream.put()
        self.redirect(original_url)

class DisplayPhotos(webapp2.RequestHandler):
    def get(self):
        unquoted_url = urllib.unquote(self.request.url)
        stream_name = re.findall('=(.*)==', unquoted_url)[0]
        user_nickname = re.findall('==(.*)', unquoted_url)[0]
        stream = Stream.query(Stream.name == stream_name, Stream.owner_nickname == user_nickname).fetch()[0]
        single_visit = SingleVisit(visit_time = datetime.datetime.now())
        single_visit.put()
        stream.total_visits.append(single_visit)
        stream.total_views = len(stream.total_visits)
        stream.put()
        photos = Photo.query(ancestor = stream_key(stream_name)).order(-Photo.upload_date).fetch()
        go_back_url = urllib.urlencode({'stream_name' : stream_name})
        template_value = {
            'stream': stream,
            'photos': photos,
            'user': users.get_current_user(),
            'go_back_url': go_back_url
        }
        template = JINJA_ENVIRONMENT.get_template('templates/display_photos.html')
        self.response.out.write(template.render(template_value))

class SubscribeStream(webapp2.RequestHandler):
    def post(self):
        original_url = self.request.headers['Referer']
        unquoted_url = urllib.unquote(original_url)

        stream_name = re.findall('=(.*)==', unquoted_url)[0]
        user_nickname = re.findall('==(.*)\?', unquoted_url)[0]

        stream = Stream.query(Stream.name == stream_name, Stream.owner_nickname == user_nickname).fetch()[0]
        user = users.get_current_user()
        if user:
            if user.nickname() not in stream.subscribers:
                stream.subscribers.append(user.nickname())
        stream.put()

        self.redirect(original_url)

class DeletePhotos(webapp2.RequestHandler):
    def post(self):
        original_url = self.request.headers['Referer']
        # stream_name=re.findall('=(.*)%3D%3D',original_url)[0]
        unquoted_url = urllib.unquote(original_url)
        stream_name = re.findall('=(.*)==',unquoted_url)[0]
        stream = Stream.query(Stream.name == stream_name, Stream.owner == users.get_current_user()).fetch()[0]
        photos2delete = self.request.get_all("photos2delete")
        if len(photos2delete) > 0:
            photos = Photo.query(Photo.id.IN(photos2delete), ancestor = stream_key(stream_name))
            ndb.delete_multi([p.key for p in photos])
            stream.pic_num = stream.pic_num - len(photos2delete)
            stream.put()
        # weird behavior
        stream.put()

        self.redirect(original_url)

app = webapp2.WSGIApplication(
    [
        ('/stream.*', ViewSingleStreamPage),
        ('/upload', Upload),
        ('/img.*', Image),
        ('/show_more.*', DisplayPhotos),
        ('/subscribe_stream', SubscribeStream),
        ('/delete_photos', DeletePhotos)
    ], debug=True)