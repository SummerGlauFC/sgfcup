from __future__ import division, print_function, absolute_import
__version__ = '0.1'
from bottle import Bottle, TEMPLATE_PATH
from project import config
app = Bottle()
TEMPLATE_PATH.append(
    config.Settings['directories']['template_base'] + '/project/views/')
TEMPLATE_PATH.remove("./views/")
from project.controllers import *
