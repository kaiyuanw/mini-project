__author__ = 'Kaiyuan_Wang'

from google.appengine.ext import ndb

class SingleVisit(ndb.Model):
    visit_time = ndb.DateTimeProperty()

class Stream(ndb.Model):
    name = ndb.StringProperty()
    tags = ndb.StringProperty(repeated=True)
    subscribers = ndb.StringProperty(repeated=True)
    cover_url = ndb.StringProperty()
    create_time = ndb.DateTimeProperty()
    update_time = ndb.DateTimeProperty()
    stream_url = ndb.StringProperty()
    guest_url = ndb.StringProperty()
    pic_num = ndb.IntegerProperty()
    total_views = ndb.IntegerProperty()
    total_visits = ndb.StructuredProperty(SingleVisit, repeated=True)
    owner = ndb.UserProperty()
    owner_nickname = ndb.StringProperty()

class Photo(ndb.Model):
    id = ndb.StringProperty()
    image = ndb.BlobProperty()
    image_key = ndb.BlobKeyProperty()
    upload_date = ndb.DateTimeProperty()
    latitude = ndb.FloatProperty()
    longitude = ndb.FloatProperty()

class EmailTimer(ndb.Model):
    email = ndb.StringProperty()
    counter = ndb.IntegerProperty()
    threshold = ndb.IntegerProperty()

class MailingList(ndb.Model):
    report_subscribers = ndb.StringProperty(repeated=True)