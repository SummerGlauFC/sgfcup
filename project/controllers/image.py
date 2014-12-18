# -*- coding: utf-8 -*-
from project import app, config
from bottle import template, request, static_file, abort

# This file is responsible for the serving of images, and also thumbnails


@app.route('/api/thumb/<url>', method='GET')
def api_thumb(url):
    # thumbnail code here
    return 'Not implemented.'


@app.route('/<url>')
@app.route('/<url>.<ext>')
def image_view(url, ext=None):
    results = config.db.fetchone(
        'SELECT * FROM `files` WHERE `shorturl` = %s', [url])

    if ext and ('.' + ext is not results["ext"]):
        abort(404, 'File not found.')
    else:
        return static_file(results["shorturl"] + results["ext"], root='/var/www/sgfcup/img/p')
