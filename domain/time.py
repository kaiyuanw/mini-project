__author__ = 'Kaiyuan_Wang'

import datetime

def get_current_us_central_time():
    return datetime.datetime.now() - datetime.timedelta(hours = 5)

def time_delta(**kwargs):
    return datetime.timedelta(**kwargs)

def get_us_central_time(time_repr):
    return datetime.datetime.strptime(time_repr,'%Y-%m-%dT%H:%M:%S.%fZ') - datetime.timedelta(hours = 5)