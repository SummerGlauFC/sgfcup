# -*- coding: utf-8 -*-
from project import app, config, functions
from bottle import request, static_file, abort, redirect, response
from bottle import jinja2_view as view, jinja2_template as template
import os
from PIL import Image, ImageOps
import magic


@app.route('/api/thumb/<url>')
@app.route('/api/thumb/<url>.<ext>')
def api_thumb(url, ext=None):
    if 'thumb_' + url + '.jpg' in os.listdir(config.Settings['directories']['thumbs']):
        return static_file('thumb_' + url + '.jpg',
                           root=config.Settings['directories']['thumbs'])
    else:
        results = config.db.fetchone(
            'SELECT * FROM `files` WHERE BINARY `shorturl` = %s', [url])

        if results:
            if ext and ('.' + ext != results["ext"]):
                abort(404, 'File not found.')
            else:
                size = 400, 400
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
        'SELECT * FROM `files` WHERE BINARY `shorturl` = %s', [url])

    if results:
        if ext and ('.' + ext != results["ext"]):
            abort(404, 'File not found.')
        else:
            if results["ext"] == 'paste':
                redirect('/paste/%s' % url)
            else:
                config.db.execute(
                    'UPDATE `files` SET hits=hits+1 WHERE `id`=%s', [results["id"]])
                if config.Settings["use_nginx_sendfile"]:
                    filename = results["shorturl"] + results["ext"]
                    file_path = config.Settings[
                        "directories"]["files"] + filename
                    response.set_header(
                        'Content-Type', magic.from_file(file_path, mime=True))
                    response.set_header('Content-Disposition',
                                        'inline; filename="{0}"'.format(results["original"]))
                    response.set_header('X-Accel-Redirect',
                                        '/get_image/{0}'.format(filename))
                    return 'nginx :)'
                else:
                    return static_file(results["shorturl"] + results["ext"],
                                       root=config.Settings["directories"]["files"])
    else:
        abort(404, 'File not found.')


@app.route('/paste/<url>')
@app.route('/paste/<url>/<flag>')
@app.route('/paste/<url>/<flag>.<ext>')
def paste_view(url, flag=None, ext=None):
    SESSION = request.environ.get('beaker.session')

    results = config.db.fetchone(
        'SELECT * FROM `files` WHERE BINARY `shorturl` = %s', [url])

    if results:
        paste_row = config.db.fetchone(
            'SELECT * FROM `pastes` WHERE `id` = %s', [results["original"]])

        revisions_rows = config.db.fetchall(
            'SELECT * FROM `revisions` WHERE `pasteid` = %s AND `fork` = 0',
            [paste_row["id"]])

        config.db.execute(
            'UPDATE `files` SET hits=hits+1 WHERE `id`=%s', [results["id"]])

        is_owner = (paste_row["userid"] == SESSION.get("id", 0))

        if flag == "raw":
            response.content_type = 'text/plain; charset=utf-8'
            return paste_row["content"]
        else:
            revisions_row = config.db.fetchone(
                'SELECT * FROM `revisions` WHERE `commit`=%s',
                [flag])

            revision = {}

            if paste_row["name"]:
                title = 'Paste "%s" (%s)' % (paste_row["name"], url)
            else:
                title = 'Paste %s' % url

            if revisions_row:
                paste_row["content"] = revisions_row["paste"]
                revision = revisions_row

                revision["parent_url"] = config.db.fetchone(
                    'SELECT * FROM `pastes` WHERE `id` = %s', [revision["parent"]])["shorturl"]

                title += " (revision %s)" % revision["commit"]

            lang = paste_row['lang']
            content = functions.highlight(paste_row["content"], lang)
            length = len(paste_row["content"])
            lines = len(paste_row["content"].split('\n'))
            hits = results["hits"]
            css = functions.css()

            if SESSION.get('id'):
                key = SESSION.get('key')
                password = SESSION.get('password')
            else:
                key = functions.id_generator(15)
                password = functions.id_generator(15)

            edit = (flag == "edit")

            return template('paste', title=title, content=content, css=css,
                            url=url, lang=lang, length=length,
                            hits=hits, lines=lines, edit=edit,
                            raw_paste=paste_row["content"], is_owner=is_owner,
                            key=key, password=password, id=paste_row["id"],
                            revisions=revisions_rows, revision=revision)
    else:
        abort(404, 'File not found.')
