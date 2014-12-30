# -*- coding: utf-8 -*-
from project import app, config
from bottle import template, request, static_file, abort
import os
from PIL import Image, ImageOps


@app.route('/api/thumb/<url>')
@app.route('/api/thumb/<url>.<ext>')
def api_thumb(url, ext=None):
    if 'thumb_' + url + '.jpg' in os.listdir(config.Settings['directories']['thumbs']):
        return static_file('thumb_' + url + '.jpg',
                           root=config.Settings['directories']['thumbs'])
    else:
        results = config.db.fetchone(
            'SELECT * FROM `files` WHERE `shorturl` = %s', [url])

        if results:
            if ext and ('.' + ext is not results["ext"]):
                abort(404, 'File not found.')
            else:
                size = 200, 200
                base = Image.open(
                    config.Settings['directories']['files'] + results["shorturl"] + results["ext"])
                image_info = base.info
                if base.mode not in ("L", "RGBA"):
                    base = base.convert("RGBA")
                base = ImageOps.fit(base, size, Image.ANTIALIAS)
                base.save(config.Settings['directories']['thumbs']
                          + 'thumb_' + url + '.jpg', **image_info)
                return static_file('thumb_' + url + '.jpg',
                                   root=config.Settings['directories']['thumbs'])
        else:
            abort(404, 'File not found.')


@app.route('/<url>')
@app.route('/<url>.<ext>')
def image_view(url, ext=None):
    results = config.db.fetchone(
        'SELECT * FROM `files` WHERE `shorturl` = %s', [url])

    if results:
        if ext and ('.' + ext is not results["ext"]):
            abort(404, 'File not found.')
        else:
            config.db.execute(
                'UPDATE `files` SET hits=hits+1 WHERE `id`=%s', [results["id"]])
            return static_file(results["shorturl"] + results["ext"],
                               root=config.Settings["directories"]["files"])
    else:
        abort(404, 'File not found.')
