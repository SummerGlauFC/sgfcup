#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from project import app
from bottle import debug, run
from beaker.middleware import SessionMiddleware
import sys

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 60 * 60 * 24 * 365 * 10,
    'session.data_dir': './data',
    'session.auto': True
}
app = SessionMiddleware(app, session_opts)

debug(True)
if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
        run(app, reloader=False, host='0.0.0.0', port=port, server='bjoern')
    except Exception as e:
        print e
        print 'Port to run on not specified.'