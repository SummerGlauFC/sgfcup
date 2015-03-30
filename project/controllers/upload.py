# -*- coding: utf-8 -*-
from project import app, config, functions
from bottle import template, request, response
import random
import re
import os
from mimetypes import guess_extension
import magic
import json
import hashlib


# File upload endpoint.
# puush api integration
@app.route('/api/auth', method='POST')
def puush_auth():
    key = request.forms.get('e', '')
    password = request.forms.get('p', '')
    hash = request.forms.get('k', '')

    user = config.db.fetchone(
        'SELECT * FROM `accounts` WHERE `key`=%s', [key])

    hash = hash if hash else hashlib.md5(key + password).hexdigest()
    print 'key: {}, password: {}, hash: {}'.format(key, password, hash)

    is_authed = False

    # If it does, check their password OR hash is correct.
    if user:
        is_authed = (user["password"] == password or user["hash"] == hash)
        user_id = user["id"]
    else:
        # If the account doesn't exist, make a new account.
        new_account = config.db.insert(
            'accounts', {"key": key,
                         "password": password,
                         "hash": hash
                         }
        )
        user_id = new_account.lastrowid
        is_authed = True

    if is_authed:
        user = config.db.fetchone(
            'SELECT * FROM `accounts` WHERE `id`=%s', [user_id])

        if user and not user["hash"]:
            config.db.execute("UPDATE `accounts` SET `hash`=%s WHERE `id`=%s",
                              [hash, user_id])

        return "1,{},,0".format(hash)
    else:
        return '-1'


@app.route('/api/up', method='POST')
def puush_up():
    k = request.forms.get('k', '')
    f = request.files.get('f', '')

    print k, request.forms.get('c', '')

    user = config.db.fetchone(
        'SELECT * FROM `accounts` WHERE `hash`=%s', [k])

    if user:
        return api_upload_file('file', {
            "key": user["key"], "password": user["password"], "file": f}, puush=True)
    else:
        print 'we fucked up'
        return '-1'


@app.route('/api/hist', method='POST')
def puush_up():
    k = request.forms.get('k', '')

    user = config.db.fetchone(
        'SELECT * FROM `accounts` WHERE `hash`=%s', [k])

    ret = "0\n"
    res = config.db.fetchall(
        'SELECT * FROM `files` WHERE `userid` = %s ORDER BY `date` DESC LIMIT 10', user["id"])

    protocol = 'http'

    if request.environ.get('HTTP_HOST') == "puush.me":
        host = config.Settings['directories']['url']
    else:
        host = request.environ.get('HTTP_HOST')

    if res:
        for row in res:
            formats = dict(
                id=row["id"], date=row["date"].strftime('%Y-%m-%d %H:%M:%S'),
                url="{}://{}/{}".format(protocol, host, row["shorturl"]),
                original=row["original"].replace(',', '_'), hits=row["hits"])
                
            ret += "{id},{date},{url},{original},{hits},0\n".format(**formats)

    return ret


@app.route('/api/upload', method='POST')
@app.route('/api/upload/<upload_type>', method='POST')
def api_upload_file(upload_type='file', form=None, puush=False):
    SESSION = request.environ.get('beaker.session')

    # All user submitted data
    if not form:
        form = {
            "key": request.forms.get('key', False),
            "password": request.forms.get('password', False),
            "file": request.files.get('files')
        }

    # Short references
    id_generator = functions.id_generator
    key = form["key"]
    password = form["password"]
    directory = config.Settings["directories"]["files"]

    # Generated random file name
    random_name = id_generator(random.SystemRandom().randint(4, 7))
    # If the user is uploading anonymously
    is_anon = (not key and not password)
    is_authed = False
    use_extensions = False

    errors = ''

    # Generate a random string for anon uploads
    if is_anon:
        key = id_generator(15)
        password = id_generator(15)

    # Returns JSON to the homepage/ShareX
    response.content_type = 'application/json; charset=utf-8'

    # Keys must only contain alphanumerics and underscores/hyphens
    if re.match("^[a-zA-Z0-9_-]+$", key):
        # Check if user has provided a file to upload or is not uploading a
        # file.
        if form["file"] or upload_type is not "file":
            if not is_anon:
                # Check if the specified account already exists.
                user = config.db.fetchone(
                    'SELECT * FROM `accounts` WHERE `key`=%s', [key])

                # If it does, check their password is correct.
                if user:
                    is_authed = (user["password"] == password)
                    user_id = user["id"]
                else:
                    # If the account doesn't exist, make a new account.
                    new_account = config.db.insert(
                        'accounts', {"key": key, "password": password})
                    user_id = new_account.lastrowid
                    is_authed = True
            else:
                is_authed = True

            if not is_authed:
                errors += 'Incorrect Key or password. '

                # Exit abruptly.
                response.status = 500
                return {
                    "success": False,
                    "error": errors
                }
            else:
                if not is_anon:
                    # Store the users credentials in a session cookie.
                    SESSION["key"] = key
                    SESSION["password"] = password
                    SESSION["id"] = user_id

                user_id = 1 if is_anon else SESSION["id"]

                if upload_type == 'file':
                    # Get filename of the upload, and split it for extension.
                    filename = form["file"].filename
                    name, ext = os.path.splitext(filename)
                    buff = None

                    # Guess the file extension if none is provided.
                    if not ext:
                        buff = form["file"].file.read()
                        ext = guess_extension(
                            magic.from_buffer(buff, mime=True))

                    # If a buffer is used, write directly to a file
                    # else use bottle's method to save a file
                    if buff:
                        with open(directory + random_name + ext, 'w') as fout:
                            fout.write(buff)
                    else:
                        form["file"].save(directory + random_name + ext)

                    # Use the base user id if the user is uploading anonymously

                    file_id = config.db.insert(
                        'files', {"userid": user_id, "shorturl": random_name,
                                  "ext": ext, "original": filename,
                                  "size": os.path.getsize(directory + random_name + ext)}).lastrowid

                    # Decide whether to return a https URL or not
                    # protocol = 'https' if config.Settings["ssl"] else 'http'

                    protocol = 'http'

                    if puush:
                        host = config.Settings['directories']['url']
                    else:
                        host = request.environ.get('HTTP_HOST')

                    print host, config.Settings['directories']['url'], request.environ.get('HTTP_HOST')

                    host = '{}://{}'.format(
                        protocol, host)

                    # Check if user has selected to show extensions
                    # in their URLs.
                    if not is_anon:
                        use_extensions = config.user_settings.get(
                            SESSION["id"], "ext")

                elif upload_type == 'paste':
                    paste_body = request.forms.get('paste_body')
                    paste_lang = request.forms.get('lang', 'text')
                    paste_name = request.forms.get('paste_name', random_name)

                    if paste_body:
                        # Reject pastes longer than 65000 characters
                        if len(paste_body) > 65000:
                            return {
                                "success": False,
                                "error": "Your paste exceeds the maximum character length of 65000"
                            }

                        paste_id = config.db.insert(
                            'pastes', {"userid": user_id,
                                       "shorturl": random_name,
                                       "name": paste_name, "lang": paste_lang,
                                       "content": paste_body}).lastrowid

                        file_id = config.db.insert(
                            'files', {"userid": user_id,
                                      "shorturl": random_name,
                                      "ext": 'paste', "original": paste_id,
                                      "size": len(paste_body)}).lastrowid
                else:
                    # The type the user provided doesn't exist.
                    return {
                        "success": False,
                        "error": "This upload type does not exist."
                    }

                # Use extensions if user has specified it in their settings.
                if not upload_type == 'paste' and use_extensions:
                    random_name = random_name + ext

                # Only return JSON if it was requested by javascript.
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return json.dumps({
                        "success": True,
                        "error": False,
                        "url": '/' + ('' if upload_type == 'file' else upload_type + '/') + random_name,
                        "key": 'anon' if is_anon else key,
                        "base": host
                    })
                else:
                    response.content_type = 'text/html; charset=utf-8'
                    if puush:
                        return "0,{},{},0".format(host + '/' + random_name, file_id)
                    return host + '/' + random_name
        else:
            if puush:
                return '-1'
            return {
                "success": False,
                "error": errors
            }
    else:
        if puush:
            return '-1'
        return {
            "success": False,
            "error": 'Invalid key given. (can only contain letters, numbers, underscores and hyphens)'
        }


@app.route('/api/edit/paste', method='POST')
def api_edit_paste():
    SESSION = request.environ.get('beaker.session')

    form = {
        "key": request.forms.get('key', False),
        "password": request.forms.get('password', False),
        "paste": request.forms.get('paste_edit_body', False),
        "id": request.forms.get('id', False),
        "commit": request.forms.get('commit', False)
    }

    is_anon = (not form["key"] and not form["password"])

    # Generate random credentials if user is uploading anonymously.
    if is_anon:
        form["key"] = functions.id_generator(15)
        form["password"] = functions.id_generator(15)

    # Generate paste name
    random_name = functions.id_generator(random.SystemRandom().randint(4, 7))

    # Select the paste that is being edited
    paste_row = config.db.fetchone(
        'SELECT * FROM `pastes` WHERE `id` = %s', [form["id"]])

    is_authed = True
    revision_row = False

    user_row = config.db.fetchone(
        'SELECT * FROM `accounts` WHERE `key`=%s', [form["key"]])

    # Check credentials for user if they exist, else make a new account.
    if not is_anon:
        if user_row:
            is_authed = (user_row["password"] == form["password"])
            user_id = user_row["id"]
        else:
            new_account = config.db.insert(
                'accounts', {"key": form["key"], "password": form["password"]})
            user_id = new_account.lastrowid

            user_row = {"id": user_id}

    if is_authed:
        # Generate a hash for the paste revision
        commit = hashlib.sha1(form["paste"]).hexdigest()[0:7]

        # Try see if this revision already exists
        try:
            revision_row = config.db.fetchone(
                'SELECT * FROM `revisions` WHERE `commit`=%s', [commit])
        except:
            revision_row = False

        # Check whether to fork or just edit the paste
        is_fork = True if not user_row else (
            user_row["id"] != paste_row["userid"])

        # Reject long pastes
        if len(form["paste"]) > 65000:
            return json.dumps({
                "success": False,
                "error": "Your paste exceeds the maximum character length of 65000"
            })
        else:
            if paste_row and user_row and not revision_row:
                # Set credentials for an account in case they changed
                if not is_anon:
                    SESSION["key"] = form["key"]
                    SESSION["password"] = form["password"]
                    SESSION["id"] = user_row["id"]

                if is_fork:
                    # Insert into pastes as well as the users gallery as a fork
                    paste_id = config.db.insert(
                        'pastes', {"userid": user_row["id"], "shorturl": random_name,
                                   "name": paste_row["name"],
                                   "lang": paste_row["lang"],
                                   "content": form["paste"]}).lastrowid

                    config.db.insert(
                        'files', {"userid": user_row["id"],
                                  "shorturl": random_name,
                                  "ext": 'paste', "original": paste_id})

                # Insert as a revision regardless of being a fork or edit
                config.db.insert(
                    'revisions', {"pasteid": paste_row["id"] if not is_fork else paste_id,
                                  "userid": user_row["id"],
                                  "commit": commit,
                                  "message": form["commit"],
                                  "paste": form["paste"],
                                  "fork": is_fork,
                                  "parent": paste_row["id"]})

                # Return data as JSON to javascript
                return json.dumps({
                    "success": True,
                    "error": False,
                    "url": '/paste/' + paste_row["shorturl"] + '.' + commit if not is_fork else '/paste/%s' % random_name,
                    "key": 'anon' if is_anon else form["key"],
                    "base": config.Settings["directories"]["url"]
                })
            else:
                return "An error has occured."
    else:
        return "An error has occured."
