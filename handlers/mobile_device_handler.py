__author__ = 'Kaiyuan_Wang'

import webapp2
import json
import urllib
import re
import uuid
from domain.model import Stream
from domain.model import Photo
from domain.model import SingleVisit
from domain.key_pool import stream_key
from domain import time
from google.appengine.api import images
from search_handler import relevant_score
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from math import sin, cos, sqrt, atan2, radians

class MobileViewAllStreams(webapp2.RequestHandler):
    def get(self):
        streams = Stream.query().order(-Stream.create_time).fetch()
        all_streams = []
        for stream in streams[:16]:
            any_stream = {}
            any_stream['stream_name'] = stream.name
            any_stream['create_time'] = str(stream.create_time)
            any_stream['cover_url'] = stream.cover_url
            all_streams.append(any_stream)
        json_obj = json.dumps({'streams':all_streams})
        self.response.write(json_obj)

class MobileShowResult(webapp2.RequestHandler):
    def get(self):
        unquoted_url = urllib.unquote(self.request.url).replace('+', ' ')
        keyword = re.findall('search_keyword=(.*)', unquoted_url)[0]
        name_list = []
        for stream in Stream.query().fetch():
            name_list.append(stream.name)
        relevant_scores = []
        for name in name_list:
            relevant_scores.append(relevant_score(name, keyword))
        sorted_mapping = sorted(zip(relevant_scores, name_list), reverse=True)
        most_relevant_names = [mapping[1] for mapping in sorted_mapping if mapping[0] != 0]
        if most_relevant_names == []:
            most_relevant_names = ['']
        result_streams = Stream.query(Stream.name.IN(most_relevant_names)).fetch()
        results = []
        for result_stream in result_streams:
            any_stream = {}
            any_stream['stream_name'] = result_stream.name
            any_stream['cover_url'] = result_stream.cover_url
            results.append(any_stream)
        json_obj = json.dumps({'streams':results})
        self.response.write(json_obj)

class MobileViewSingleStreamPage(webapp2.RequestHandler):
    def get(self):
        unquoted_url = urllib.unquote(self.request.url).replace('+', ' ')
        stream_name = re.findall('=(.*)\?', unquoted_url)[0]
        user_name = re.findall('\?(.*)', unquoted_url)[0]
        streams = Stream.query(Stream.name == stream_name).fetch()
        if len(streams) > 0:
            stream = streams[0]
            if stream.owner.email() != user_name:
                single_visit = SingleVisit(visit_time=time.get_current_us_central_time())
                single_visit.put()
                stream.total_visits.append(single_visit)
                stream.total_views = len(stream.total_visits)
            stream.put()
            photos = Photo.query(ancestor=stream_key(stream_name)).order(-Photo.upload_date).fetch()
            results = []
            for photo in photos:
                any_photo = {}
                any_photo['image_url'] = images.get_serving_url(photo.image_key)
                any_photo['caption'] = photo.caption
                results.append(any_photo)
            json_obj = json.dumps({'photos':results, 'owner':stream.owner.email()})
            self.response.write(json_obj)

class MobileGetUploadURL(webapp2.RequestHandler):
    def get(self, stream_name):
        upload_url = blobstore.create_upload_url('/mobile_upload_handler/%s' % stream_name)
        upload_url = str(upload_url)
        result_url = {'upload_url': upload_url}
        jsonObj = json.dumps(result_url)
        self.response.write(jsonObj)

class MobileUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, stream_name):
        stream = Stream.query(Stream.name == stream_name).fetch()[0]
        image = self.get_uploads()[0]
        img_key = image.key()
        location = self.request.params['location']
        geoLocation = location.split('_')
        photo = Photo(upload_date=time.get_current_us_central_time(), image_key=img_key, parent=stream_key(stream_name))
        stream.update_time = photo.upload_date
        stream.pic_num = stream.pic_num + 1
        photo.id = str(uuid.uuid4())
        photo.image = str(image)
        photo.latitude = float(geoLocation[0])
        photo.longitude = float(geoLocation[1])
        photo.caption = self.request.params['photoCaption']
        photo.put()
        stream.put()

class MobileSubscribedStream(webapp2.RequestHandler):
    def get(self, user_email):
        results = []
        unquoted_user_email = urllib.unquote(user_email)
        subscribed_streams = Stream.query(Stream.subscribers == unquoted_user_email).fetch()
        if len(subscribed_streams) == 0:
            subscribed_streams = Stream.query(Stream.subscribers == unquoted_user_email.split('@')[0]).fetch()
        subscribed_photos = []
        subscribed_photo_stream_names = []
        for subscribed_stream in subscribed_streams:
            new_photos = Photo.query(ancestor=stream_key(subscribed_stream.name)).fetch()
            subscribed_photos += new_photos
            subscribed_photo_stream_names += [subscribed_stream.name for _ in range(len(new_photos))]
        subscribed_photo_infos = sorted(zip(subscribed_photos, subscribed_photo_stream_names), key=lambda x: str(x[0].upload_date), reverse=True)
        for photo_info in subscribed_photo_infos[:16]:
            any_photo = {}
            any_photo['caption'] = photo_info[0].caption
            any_photo['upload_date'] = str(photo_info[0].upload_date)
            any_photo['image_url'] = images.get_serving_url(photo_info[0].image_key)
            any_photo['stream_name'] = photo_info[1]
            results.append(any_photo)
        json_obj = json.dumps({'photos':results})
        self.response.write(json_obj)

class MobileNearbyPhotos(webapp2.RequestHandler):
    def get(self, current_location):
        coordinator = current_location.split('_')
        lat = float(coordinator[0])
        lon = float(coordinator[1])
        results = []
        streams = Stream.query().fetch()
        for stream in streams:
            photos = Photo.query(ancestor=stream_key(stream.name))
            for photo in photos:
                any_photo = {}
                any_photo['image_url'] = images.get_serving_url(photo.image_key)
                any_photo['stream_name'] = stream.name
                plat = float(photo.latitude)
                plon = float(photo.longitude)
                R = 6373.0

                lat1 = radians(lat)
                lon1 = radians(lon)
                lat2 = radians(plat)
                lon2 = radians(plon)

                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = (sin(dlat / 2)) ** 2 + cos(lat1) * cos(lat2) * (sin(dlon / 2)) ** 2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                distance = R * c
                any_photo["actual_distance"] = distance
                if distance > 10:
                    any_photo["str_distance"] = str(distance).split('.', 1)[0] + 'km'
                else:
                    any_photo["str_distance"] = str(distance * 1000).split('.', 1)[0] + 'm'
                results.append(any_photo)
        results = sorted(results, key=lambda x: x['actual_distance'])
        json_obj = json.dumps({'photos':results})
        self.response.write(json_obj)

app = webapp2.WSGIApplication(
    [
        ('/mobile_view_all_stream', MobileViewAllStreams),
        ('/mobile_show_result.*', MobileShowResult),
        ('/mobile_stream_name.*', MobileViewSingleStreamPage),
        ('/mobile_get_upload_url/([^/]+)', MobileGetUploadURL),
        ('/mobile_upload_handler/([^/]+)', MobileUploadHandler),
        ('/mobile_subscribed_streams/([^/]+)', MobileSubscribedStream),
        ('/mobile_nearby_photos/([^/]+)', MobileNearbyPhotos)
    ], debug=True)