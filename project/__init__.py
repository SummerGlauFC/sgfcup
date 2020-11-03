import sentry_sdk
from flask import Flask
from flask import g
from flask import render_template
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.local import LocalProxy

from db import DB
from project import config
from project.functions import Error
from project.functions import RegexConverter
from project.functions import connect_db
from project.functions import get_setting
from project.usersettings import UserSettings

debug = bool(get_setting("debug.enabled"))
sentry_enabled = bool(get_setting("debug.sentry.enabled"))

# logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
__version__ = "0.1"
app = Flask(__name__, template_folder="views")

if sentry_enabled:
    sentry_sdk.init(
        dsn=get_setting("debug.sentry.url"), integrations=[FlaskIntegration()]
    )

# allow regex for URL matching
app.url_map.converters["regex"] = RegexConverter

# add config values that are used by flask
app.config.update(
    DEBUG=debug,
    SECRET_KEY=get_setting("sessions.encrypt_key"),
    PREFERRED_URL_SCHEME="https" if get_setting("ssl") else "http",
    MAX_CONTENT_LENGTH=get_setting("max_file_size"),
)


@app.context_processor
def inject_funcs():
    from project.constants import FileType
    from project.constants import PasteAction
    from project.constants import search_modes
    from project.constants import sort_modes
    from project.functions import url_for_page

    return {
        "sort_modes": sort_modes,
        "search_modes": search_modes,
        "file_type": FileType,
        "paste_actions": PasteAction,
        "url_for_page": url_for_page,
    }


def get_db():
    if not hasattr(g, "db"):
        g.db = connect_db()
    return g.db


def get_user_settings():
    # always reload the settings file when in debug
    if app.debug:
        return UserSettings("project/user_settings.json", get_db())

    if not hasattr(g, "user_settings"):
        g.user_settings = UserSettings("project/user_settings.json", get_db())
    return g.user_settings


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop("db", None)
    # noinspection PyUnusedLocal
    user_settings = g.pop("user_settings", None)

    if db is not None:
        db.close()


db: DB = LocalProxy(get_db)  # noqa
user_settings: UserSettings = LocalProxy(get_user_settings)  # noqa

from project.controllers import *  # noqa


@app.errorhandler(404)
def error_not_found(err):
    return render_template("error.tpl", in_title=True, error=err.name, status=err.code)


# handle request entity too large
@app.errorhandler(413)
def error_too_large(err):
    return Error("File too large", status=err.code).response()


@app.errorhandler(Error)
def error_api(err: Error):
    return err.response()
