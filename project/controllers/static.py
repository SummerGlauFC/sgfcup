# -*- coding: utf-8 -*-
from project import app, functions
from bottle import static_file, request
from bottle import jinja2_view as view, jinja2_template as template


@app.route('/')
@view('index.tpl')
def index():
    SESSION = request.environ.get('beaker.session')

    if SESSION.get('id'):
        return {"key": SESSION.get('key'), "password": SESSION.get('password')}
    else:
        return {"key": functions.id_generator(15), "password": functions.id_generator(15)}


@app.get('/paste')
@view('pastebin.tpl')
def paste_home():
    SESSION = request.environ.get('beaker.session')

    if SESSION.get('id'):
        return {"key": SESSION.get('key'), "password": SESSION.get('password')}
    else:
        return {"key": functions.id_generator(15), "password": functions.id_generator(15)}


@app.route('/keys')
def keys():
    SESSION = request.environ.get('beaker.session')

    return template(
        'general',
        title='Keys',
        message='Key: ' + SESSION.get('key', 'Not set.') +
        '<br />Password: ' + SESSION.get('password', 'Not set.'),
    )


@app.route('/:file#(favicon.ico)#')
def favicon(file):
    return static_file(file, root='project/static/misc')


@app.route('/static/css/<file>')
def server_static(file):
    return static_file(file, root='project/static/css')
