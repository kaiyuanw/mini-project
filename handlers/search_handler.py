__author__ = 'Kaiyuan_Wang'

import urllib
import re
import webapp2

from google.appengine.api import users

from domain import jinja_env
from domain.model import Stream


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
        unquoted_url = urllib.unquote(self.request.url)
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
        print '--------'
        print (len(result_streams))
        print(result_streams)
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
    for  i in xrange(len(stringa)):
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

app = webapp2.WSGIApplication(
    [
        ('/search_streams', SearchPage),
        ('/show_result', ShowResult)
    ], debug=True)