__author__ = 'Kaiyuan_Wang'

import webapp2
from google.appengine.api import users
from google.appengine.api import mail

from domain import jinja_env, time
from domain.model import Stream
from domain.model import EmailTimer
from domain.model import SingleVisit
from domain.key_pool import email_timer_key


JINJA_ENVIRONMENT = jinja_env.get_jinja_env()

class TrendingPage(webapp2.RequestHandler):
    def get(self):
        streams = Stream.query().fetch()
        most_three_popular_streams = sorted(streams, key = lambda stream: len(stream.total_visits), reverse = True)[:3]
        timer = get_timer('timer')
        template_value = {
                'most_three_popular_streams': most_three_popular_streams,
                'timer': timer
        }
        template = JINJA_ENVIRONMENT.get_template('templates/trending_stream.html')
        self.response.out.write(template.render(template_value))

class UpdateFrequency(webapp2.RequestHandler):
    def post(self):
        original_url = self.request.headers['Referer']
        freq = self.request.get("frequency")
        timer = get_timer('timer')
        timer.threshold = get_frequency(freq)
        timer.put()
        self.redirect(original_url)

class SendEmail(webapp2.RequestHandler):
    def get(self):
        timer = get_timer('timer')
        self.response.out.write('<h>' + str(timer.counter) + '</h>')
        timer.counter = timer.counter + 1
        self.response.out.write('<h>' + str(timer.counter) + '</h>')
        if timer.counter >= timer.threshold:
            timer.counter = 0
            streams = Stream.query().fetch()
            most_three_popular_streams = sorted(streams, key = lambda stream: len(stream.total_visits), reverse = True)[:3]
            email_message = 'The most 3 popular streams are '
            prefix = ''
            for stream in most_three_popular_streams:
                email_message += (prefix + stream.name + ' owned by ' + stream.owner_nickname)
                prefix = ', '
            email_subject = 'Trending Stream Report'
            if users.get_current_user():
                email_sender = users.get_current_user().email()
            else:
                email_sender = 'wangkaiyuanzz@gmail.com'
            mail.send_mail(
                sender = email_sender,
                to = 'wangkaiyuanzz@gmail.com',
                subject = email_subject,
                body = email_message
            )
            mail.send_mail(
                sender = email_sender,
                to = 'xingyuan.wang.zju@gmail.com',
                subject = email_subject,
                body = email_message
            )
            mail.send_mail(
                sender = email_sender,
                to = email_sender,
                subject = email_subject,
                body = email_message
            )
        self.response.out.write('<h>' + str(timer.counter) + '</h>')
        self.response.out.write('<h>' + str(timer.threshold) + '</h>')
        timer.put()

class ClearVisitorHistoryPeriodically(webapp2.RequestHandler):
    def get(self):
        streams = Stream.query().fetch()
        for stream in streams:
            visitor_history = stream.total_visits
            visitors_left = []
            for visitor in visitor_history:
                if visitor.visit_time < (time.get_us_central_time() - time.time_delta(hours = 1)):
                    visit = SingleVisit.query(SingleVisit.visit_time == visitor.visit_time).fetch()[0]
                    visit.key.delete()
                else:
                    visitors_left.append(visitor)
            stream.total_visits = visitors_left
            stream.total_views = len(stream.total_visits)
            stream.put()

def get_timer(timer_name):
    # timers = EmailTimer.query(EmailTimer.name == timer_name).fetch()
    timers = EmailTimer.query(ancestor = email_timer_key(timer_name)).fetch()
    if len(timers) == 0:
        timer = EmailTimer(name = timer_name, counter = 0, threshold = 0, parent = email_timer_key(timer_name))
    else:
        timer = timers[0]
    timer.put()
    return timer

def get_frequency(freq):
    d = {'no': 0, '5m': 1, '1h': 12, '1d':288}
    return d[freq]

app = webapp2.WSGIApplication(
    [
        ('/trending_stream', TrendingPage),
        ('/update_email_freq', UpdateFrequency),
        ('/send_email', SendEmail),
        ('/clear', ClearVisitorHistoryPeriodically)
    ], debug=True)