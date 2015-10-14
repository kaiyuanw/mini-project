__author__ = 'Kaiyuan_Wang'

import urllib
import re
import webapp2
import json

from google.appengine.api import users
from google.appengine.api import search

from domain import jinja_env
from domain.model import Stream
from domain.index_pool import stream_index
from domain.suggestions import generate_suggestions

JINJA_ENVIRONMENT = jinja_env.get_jinja_env()


class SearchPage(webapp2.RequestHandler):
    def get(self):
        search_enabled = False
        template_value = {
            'search_enabled': search_enabled,
            'user': users.get_current_user(),
            'result_size': 0,
            'keyword': '',
            'result_streams': []
        }
        template = JINJA_ENVIRONMENT.get_template('templates/search_stream.html')
        self.response.out.write(template.render(template_value))


class ShowResult(webapp2.RequestHandler):
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
        five_most_relevant_names = [mapping[1] for mapping in sorted_mapping[:5] if mapping[0] != 0]
        if five_most_relevant_names == []:
            five_most_relevant_names = ['']
        result_streams = Stream.query(Stream.name.IN(five_most_relevant_names)).fetch()
        search_enabled = True
        template_value = {
            'search_enabled': search_enabled,
            'user': users.get_current_user(),
            'keyword': keyword,
            'result_streams': result_streams
        }
        template = JINJA_ENVIRONMENT.get_template('templates/search_stream.html')
        self.response.out.write(template.render(template_value))


def relevant_score(stringa, stringb):
    x = list()
    y = list()
    for i in xrange(len(stringa)):
        x.append(stringa[i])
    for j in xrange(len(stringb)):
        y.append(stringb[j])
    if (len(x) == 0 or len(y) == 0):
        return 0
    else:
        a = x[0]
        b = y[0]
        if (a == b):
            return relevant_score(x[1:], y[1:]) + 1
        else:
            return max(relevant_score(x[1:], y), relevant_score(x, y[1:]))


class AutoComplete(webapp2.RequestHandler):
    def get(self):
        unquoted_url = urllib.unquote(self.request.url).replace('+', ' ')
        keyword = re.findall('term=(.*)', unquoted_url)[0]
        name_list = []
        # for stream in Stream.query().fetch():
        # name_list.append(stream.name)
        # relevant_scores = []
        # for name in name_list:
        #     relevant_scores.append(relevant_score(name, keyword))
        # sorted_mapping = sorted(zip(relevant_scores, name_list), reverse=True)
        # twenty_most_relevant_names = sorted([mapping[1] for mapping in sorted_mapping[:20] if mapping[0] != 0])
        # result = { "data" : twenty_most_relevant_names }
        try:
            index = search.Index(name=stream_index())
            for scored_document in index.search(keyword):
                name_list.append(scored_document.field('stream_name').value)
        except search.Error as e:
            print e.message
        print sorted(name_list)
        result = sorted(name_list)[:20]
        self.response.headers['Content-Type'] = 'application/json'
        result = json.dumps(result)
        self.response.write(result)


class RebuildSearchIndex(webapp2.RequestHandler):
    def get(self):
        try:
            index = search.Index(name=stream_index())
            while True:
                doc_ids = [document.doc_id for document in index.get_range(ids_only=True)]
                if not doc_ids:
                    break
                index.delete(doc_ids)
            for stream in Stream.query().fetch():
                doc = search.Document(
                    fields=[
                        search.TextField(name='stream_name', value=stream.name),
                        search.TextField(name='suggestions', value=generate_suggestions(stream.name))
                    ]
                )
                index.put(doc)
        except search.Error as e:
            print e.message


app = webapp2.WSGIApplication(
    [
        ('/search_streams', SearchPage),
        ('/show_result', ShowResult),
        ('/auto_complete', AutoComplete),
        ('/rebuild_search_index', RebuildSearchIndex)
    ], debug=True)