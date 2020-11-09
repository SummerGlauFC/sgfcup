from flask import current_app
from flask import g
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from werkzeug.local import LocalProxy

from db import DB
from project.usersettings import UserSettings

login_manager = LoginManager()
csrf = CSRFProtect()


def get_db():
    if not hasattr(g, "db"):
        g.db = DB(pool=current_app.config["POOL"], debug=current_app.debug)
    return g.db


def get_user_settings():
    # always reload the settings file when in debug
    if current_app.debug:
        return UserSettings("project/user_settings.json", get_db())

    if not hasattr(g, "user_settings"):
        g.user_settings = UserSettings("project/user_settings.json", get_db())
    return g.user_settings


db: DB = LocalProxy(get_db)  # noqa
user_settings: UserSettings = LocalProxy(get_user_settings)  # noqa
