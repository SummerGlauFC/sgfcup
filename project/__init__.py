from datetime import timedelta

import sentry_sdk
from flask import Flask
from flask import g
from flask import render_template
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import RequestEntityTooLarge

from project import config
from project.extensions import db
from project.functions import Error
from project.functions import RegexConverter
from project.functions import create_pool
from project.functions import get_setting
from project.routes import register_routes
from project.usersettings import UserSettings

__version__ = "0.1"


def create_app() -> Flask:
    """ Create Flask app. """

    app = Flask(__name__, template_folder="views")

    configure_app(app)
    configure_extensions(app)
    configure_jinja(app)
    configure_error_handlers(app)

    register_routes(app)

    return app


def configure_app(app: Flask):
    """ Configure flask app. """

    # set up sentry logging if enabled
    sentry_enabled = bool(get_setting("debug.sentry.enabled"))
    if sentry_enabled:
        sentry_sdk.init(
            dsn=get_setting("debug.sentry.url"), integrations=[FlaskIntegration()]
        )

    # allow regex for URL matching
    app.url_map.converters["regex"] = RegexConverter

    # add config values that are used by flask
    app.config.update(
        DEBUG=bool(get_setting("debug.enabled")),
        SECRET_KEY=get_setting("sessions.encrypt_key"),
        PREFERRED_URL_SCHEME="https" if get_setting("ssl") else "http",
        MAX_CONTENT_LENGTH=get_setting("max_file_size"),
        POOL=create_pool(),
        PERMANENT_SESSION_LIFETIME=timedelta(days=365),
        USE_SESSION_FOR_NEXT=False,
    )


def configure_extensions(app: Flask):
    """ Configure flask app extensions. """
    from project.extensions import login_manager
    from project.extensions import csrf
    from project.services.account import (
        AccountService,
        AnonymousAccount,
        ANONYMOUS_ACCOUNT,
    )

    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.user_loader(AccountService.get_by_id)
    login_manager.anonymous_user = AnonymousAccount
    login_manager.login_view = "static.login"

    # remove db and user_settings when needed
    @app.teardown_appcontext
    def teardown_db(_):
        g.pop("user_settings", None)
        g_db = g.pop("db", None)
        if g_db is not None:
            g_db.close()


def configure_jinja(app: Flask):
    """ Configure jinja context and filters. """

    @app.context_processor
    def inject_funcs():
        from project.constants import FileType
        from project.constants import PasteAction
        from project.constants import search_modes
        from project.constants import sort_modes

        return {
            "sort_modes": sort_modes,
            "search_modes": search_modes,
            "file_type": FileType,
            "paste_actions": PasteAction,
        }


def configure_error_handlers(app: Flask):
    """ Configure error responses. """

    # handle API-bound errors
    @app.errorhandler(Error)
    def error_api(err: Error):
        return err.response()

    # handle request entity too large
    @app.errorhandler(RequestEntityTooLarge)
    def error_too_large(err):
        # TODO: verify change worked
        raise Error("File too large", status=err.code)

    # handle general HTTP exceptions i.e. 401, 403, 404
    @app.errorhandler(HTTPException)
    def error_not_found(err):
        return render_template(
            "error.tpl", in_title=True, error=err.name, status=err.code
        )
