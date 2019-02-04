from __future__ import absolute_import, division, print_function

from bottle import jinja2_view as view
from bottle import request, static_file

from project import app, config, functions

# File to serve (mostly) static files, like the upload pages, the
# user info page, the favicon and all stylesheets
# (provided their HTTP server doesn't serve the stylesheets/favicon)


def key_password_return(SESSION):
    SESSION = request.environ.get('beaker.session', {})

    # Check if the user has got their key and password stored, else
    # generate a mostly secure key for them.
    if SESSION.get('id'):
        return {'key': SESSION.get('key'), 'password': SESSION.get('password')}

    return {'key': functions.id_generator(15), 'password': functions.id_generator(15)}


@app.route('/')
@view('index.tpl')
def index():
    return key_password_return(request.environ.get('beaker.session'))


@app.get('/paste')
@view('pastebin.tpl')
def paste_home():
    return key_password_return(request.environ.get('beaker.session'))


@app.route('/keys')
@view('general.tpl')
def keys():
    SESSION = request.environ.get('beaker.session', {})

    settings = config.user_settings.get_all_values(SESSION.get('id', 0))

    key = SESSION.get('key', 'Not set.')
    password = SESSION.get('password', 'Not set.')
    gallery_password = settings['gallery_password']['value']
    br = '<br />'

    # Provide the user with their details.
    return {
        'title': 'Keys',
        'message': f'Key: {key}{br}Password: {password}{br}Gallery view password: {gallery_password}'
    }


@app.route('/favicon.ico')
def favicon():
    # Serve the favicon
    return static_file('favicon.ico', root='project/static/misc')


@app.route('/static/<filepath:path>')
def server_static(filepath):
    # Serve css and flush the cache when serving it with bottle.
    response = static_file(filepath, root='project/static')
    response.set_header('Cache-Control', 'no-cache')
    return response
