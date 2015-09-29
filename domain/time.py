__author__ = 'Kaiyuan_Wang'

import datetime

def get_us_central_time():
    return datetime.datetime.now() - datetime.timedelta(hours = 5)

def time_delta(**kwargs):
    return datetime.timedelta(**kwargs)