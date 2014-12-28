# -*- coding: utf-8 -*-
from project import app, config, functions
from bottle import template, request, response
import random
import re
import os
from mimetypes import guess_extension
import magic
import json

# this file is responsible for handling the upload of files, and also pastes.
# TODO: add paste handling


@app.route('/api/upload/file', method='POST')
def api_upload_file():
    SESSION = request.environ.get('beaker.session')

    form = {
        "key": request.forms.get('key', default=False),
        "password": request.forms.get('password', default=False),
        "file": request.files.get('files')
    }

    id_generator = functions.id_generator

    key = form["key"]
    password = form["password"]

    directory = config.Settings["directories"]["files"]
    random_name = id_generator(random.SystemRandom().randint(4, 7))
    is_public = (not key and not password)
    is_authed = False

    errors = ''

    if is_public:
        key = id_generator(15)
        password = id_generator(15)

    if re.match("^[a-zA-Z0-9_-]+$", key):
        if form["file"]:
            if not is_public:
                user = config.db.fetchone(
                    'SELECT * FROM `accounts` WHERE `key`=%s', [key])

                if user:
                    is_authed = (user["password"] == password)
                    user_id = user["id"]
                else:
                    new_account = config.db.insert(
                        'accounts', {'key': key, 'password': password})
                    user_id = new_account.lastrowid
                    is_authed = True
            else:
                is_authed = True

            if not is_authed:
                errors += 'Incorrect Key or password. '
            else:
                if not is_public:
                    SESSION["key"] = key
                    SESSION["password"] = password
                    SESSION["id"] = user_id

                filename = form["file"].filename
                name, ext = os.path.splitext(filename)

                if '.' not in filename:
                    name = random_name

                if ext == '':
                    buff = form["file"].file.read()
                    ext = guess_extension(magic.from_buffer(buff, mime=True))

                filename = name + ext
                if name == random_name:
                    with open(directory + name + ext, 'w') as fout:
                        fout.write(buff)
                else:
                    form["file"].save(directory + random_name + ext)

                user_id = 1 if is_public else SESSION["id"]

                config.db.insert(
                    'files', {'userid': user_id, 'shorturl': random_name, 'ext': ext, 'original': filename})

                if config.Settings["ssl"]:
                    config.Settings['directories']['url'] = 'https://' + \
                        request.environ.get('HTTP_HOST')

                if not is_public:
                    use_extensions = config.user_settings.get(
                        SESSION["id"], "ext")

                response.content_type = 'text/html; charset=utf-8'
                return json.dumps({
                    "success": True,
                    "error": False,
                    "url": '/' + random_name,
                    "key": 'anon' if is_public else key,
                    "base": config.Settings["directories"]["url"]
                })

        else:
            return {
                "success": False,
                "error": errors
            }
    else:
        return {
            "success": False,
            "error": 'Invalid key given. (can only contain letters, numbers, underscores and hyphens)'
        }
