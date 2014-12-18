#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from project import app
from bottle import debug, run
from beaker.middleware import SessionMiddleware

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 60 * 60 * 24 * 365 * 10,
    'session.data_dir': './data',
    'session.auto': True
}
app = SessionMiddleware(app, session_opts)

debug(True)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    run(app, reloader=False, host='0.0.0.0', port=port)
