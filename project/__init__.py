from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging

from bottle import Bottle
from bottle import TEMPLATE_PATH

from project import config

logging.basicConfig(
    level=logging.DEBUG if config.Settings["debug"]["enabled"] else logging.INFO
)
__version__ = "0.1"
app = Bottle()
# TEMPLATE_PATH.append(
#     config.Settings['directories']['template_base'] + './project/views/')
TEMPLATE_PATH.append("./project/views/")
TEMPLATE_PATH.remove("./views/")

from project.controllers import *
