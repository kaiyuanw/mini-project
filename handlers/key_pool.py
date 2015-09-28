__author__ = 'Kaiyuan_Wang'

from google.appengine.ext import ndb
from google.appengine.api import users

DEFAULT_USER_NICKNAME = 'default_user_nickname'
DEFAULT_STREAM_NAME = 'default_stream_name'

def user_key(nickname = DEFAULT_USER_NICKNAME):
    return ndb.Key('User', nickname)

def stream_key(name = DEFAULT_STREAM_NAME):
    return ndb.Key('Stream', name)