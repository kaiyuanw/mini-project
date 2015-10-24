__author__ = 'Kaiyuan_Wang'

import webapp2
import json
import urllib
import re
from domain.model import Stream
from domain.model import Photo
from domain.key_pool import stream_key
from google.appengine.api import images
from search_handler import relevant_score

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
        stream_name = re.findall('=(.*)', unquoted_url)[0]
        streams = Stream.query(Stream.name == stream_name).fetch()
        if len(streams) > 0:
            photos = Photo.query(ancestor=stream_key(stream_name)).order(-Photo.upload_date).fetch()
            results = []
            for photo in photos:
                any_photo = {}
                any_photo['image_url'] = images.get_serving_url(photo.image_key)
                any_photo['caption'] = photo.caption
                results.append(any_photo)
            json_obj = json.dumps({'photos':results})
            self.response.write(json_obj)

app = webapp2.WSGIApplication(
    [
        ('/mobile_view_all_stream', MobileViewAllStreams),
        ('/mobile_show_result.*', MobileShowResult),
        ('/mobile_stream_name.*', MobileViewSingleStreamPage)
    ], debug=True)