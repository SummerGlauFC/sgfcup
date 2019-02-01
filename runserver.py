#!/usr/bin/env python
from __future__ import division, print_function, absolute_import
import sys
from beaker.middleware import SessionMiddleware
from bottle import debug, run
from project.functions import nested_dict_get
from project.config import Settings
from project import app

debug_enabled = bool(nested_dict_get(Settings, 'debug.enabled'))
sentry_enabled = bool(nested_dict_get(Settings, 'debug.sentry.enabled'))
if sentry_enabled:
    from raven import Client
    from raven.contrib.bottle import Sentry


session_opts = {
    'session.type': 'cookie',
    'session.cookie_expires': False,
    'session.data_dir': './data',
    'session.auto': True,
    'session.validate_key': nested_dict_get(Settings, 'sessions.validate_key'),
    'session.encrypt_key': nested_dict_get(Settings, 'sessions.encrypt_key')
}
app = SessionMiddleware(app, session_opts)

if sentry_enabled:
    app.catchall = False
    client = Client(nested_dict_get(Settings, 'debug.sentry.url'),
                    include_paths=[__name__.split('.', 1)[0]])
    app = Sentry(app, client)

debug(debug_enabled)
if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
        run(app, reloader=False, host='0.0.0.0', port=port, server='tornado')
    except Exception as e:
        print(e)
        print('Port to run on not specified.')
