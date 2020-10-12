#!/usr/bin/env python
import sys

from beaker.middleware import SessionMiddleware
from bottle import debug
from bottle import run

from project import app
from project.functions import get_setting

debug_enabled = bool(get_setting("debug.enabled"))
sentry_enabled = bool(get_setting("debug.sentry.enabled"))
if sentry_enabled:
    from raven import Client
    from raven.contrib.bottle import Sentry

session_opts = {
    "session.type": "cookie",
    "session.cookie_expires": False,
    "session.data_dir": "./data",
    "session.auto": True,
    "session.validate_key": get_setting("sessions.validate_key"),
    "session.encrypt_key": get_setting("sessions.encrypt_key"),
}
app = SessionMiddleware(app, session_opts)

if sentry_enabled:
    app.catchall = False
    client = Client(
        get_setting("debug.sentry.url"), include_paths=[__name__.split(".", 1)[0]]
    )
    app = Sentry(app, client)

debug(debug_enabled)
if __name__ == "__main__":
    try:
        port = int(sys.argv[1])
        run(
            app,
            reloader=debug_enabled,
            host="localhost",
            port=port,
            server="tornado" if not debug_enabled else "wsgiref",
        )
    except Exception as e:
        print(e)
        print("Port to run on not specified.")
