__author__ = 'Kaiyuan_Wang'

import jinja2
import path


def get_jinja_env():
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path.get_project_path()),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)