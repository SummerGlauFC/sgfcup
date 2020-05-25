from __future__ import absolute_import, division, print_function

import logging

from bottle import TEMPLATE_PATH, Bottle

from project import config

logging.basicConfig(
    level=logging.DEBUG if config.Settings['debug']['enabled'] else logging.INFO)
__version__ = '0.1'
app = Bottle()
# TEMPLATE_PATH.append(
#     config.Settings['directories']['template_base'] + './project/views/')
TEMPLATE_PATH.append("./project/views/")
TEMPLATE_PATH.remove("./views/")

from project.controllers import admin, gallery, settings, static, upload, view
