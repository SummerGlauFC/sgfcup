import logging

from bottle import Bottle
from bottle import Jinja2Template
from bottle import TEMPLATE_PATH
from bottle import jinja2_template as template

from project import config
from project.configdefines import FileType
from project.configdefines import PasteAction

logging.basicConfig(
    level=logging.DEBUG if config.Settings["debug"]["enabled"] else logging.INFO
)
__version__ = "0.1"
app = Bottle()
TEMPLATE_PATH.append("./project/views/")
TEMPLATE_PATH.remove("./views/")

Jinja2Template.defaults = {"file_type": FileType, "paste_actions": PasteAction}
Jinja2Template.settings = {"autoescape": True}

from project.controllers import *  # noqa


@app.error(404)
def error_not_found(err):
    return template("error.tpl", in_title=True, error=err.body, status=err.status)
