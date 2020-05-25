from __future__ import absolute_import, division, print_function

import hashlib
import os
import random
import re
from mimetypes import guess_extension

import magic
from bottle import request, response

from project import app, config, functions
from project.functions import get_setting

id_generator = functions.id_generator


# File upload endpoint.
@app.route('/api/upload', method='POST')
@app.route('/api/upload/<upload_type>', method='POST')
def api_upload_file(upload_type='file', form=None):
    SESSION = request.environ.get('beaker.session', {})

    # All user submitted data
    if not form:
        form = {
            'key': request.forms.get('key', False),
            'password': request.forms.get('password', False),
            'file': request.files.files
        }

    # Short references
    key = form['key']
    password = form['password']
    files = form['file']
    directory = get_setting('directories.files')

    # Generated random file name
    random_name = id_generator(random.SystemRandom().randint(4, 7))
    is_anon = (not key)
    is_authed = False
    use_extensions = 0

    errors = ''

    # Keys must only contain alphanumerics and underscores/hyphens
    if is_anon or re.match('^[a-zA-Z0-9_-]+$', key):
        # Check if user has provided a file to upload or is not uploading a
        # file.
        if files or upload_type != 'file':
            if not is_anon:
                # Check if the specified account already exists.
                user = config.db.select(
                    'accounts', where={'key': key}, singular=True)

                # If it does, check their password is correct.
                if user:
                    is_authed = (user['password'] == password)
                    user_id = user['id']
                else:
                    # If the account doesn't exist, make a new account.
                    new_account = config.db.insert(
                        'accounts', {'key': key, 'password': password})
                    user_id = new_account.lastrowid
                    is_authed = True
            else:
                is_authed = True

            if not is_authed:
                errors += 'Incorrect Key or password. '

                # Exit abruptly.
                response.status = 403
                return functions.json_error(errors)
            else:
                if not is_anon:
                    # Store the users credentials in a session cookie.
                    SESSION['key'] = key
                    SESSION['password'] = password
                    SESSION['id'] = user_id

                user_id = 0 if is_anon else SESSION['id']

                # Decide whether to return a https URL or not
                host = '{}://{}'.format('https' if get_setting('ssl') else 'http',
                                        request.environ.get('HTTP_HOST'))

                if upload_type == 'file':
                    filename = files.filename
                    name, ext = os.path.splitext(filename)
                    buff = None

                    # Guess the file extension if none is provided.
                    if not ext:
                        # buff = files.file.read()
                        # ext = guess_extension(
                        #     magic.from_buffer(buff, mime=True))
                        ext = ""

                    # If a buffer is used, write directly to a file
                    # else use bottle's method to save a file
                    if buff:
                        with open(directory + random_name + ext, 'wb') as fout:
                            fout.write(buff)
                    else:
                        files.save(directory + random_name + ext)

                    file_id = config.db.insert(
                        'files', {'userid': user_id, 'shorturl': random_name,
                                  'ext': ext, 'original': filename,
                                  'size': os.path.getsize(directory + random_name + ext)}).lastrowid

                    if not is_anon:
                        use_extensions = config.user_settings.get(
                            user_id, 'ext')

                elif upload_type == 'paste':
                    paste_body = request.forms.get('paste_body')
                    paste_lang = request.forms.get('lang', 'text')
                    paste_name = request.forms.get('paste_name', random_name)
                    ext = 'paste'

                    if paste_body:
                        # Reject pastes longer than 65000 characters
                        if len(paste_body) > 65000:
                            return functions.json_error('Your paste exceeds the maximum character length of 65000')

                        paste_id = config.db.insert(
                            'pastes', {'userid': user_id,
                                       'shorturl': random_name,
                                       'name': paste_name,
                                       'lang': paste_lang,
                                       'content': paste_body}).lastrowid

                        file_id = config.db.insert(
                            'files', {'userid': user_id,
                                      'shorturl': random_name,
                                      'ext': ext,
                                      'original': paste_id,
                                      'size': len(paste_body)}).lastrowid
                else:
                    # The type the user provided doesn't exist.
                    return functions.json_error('This upload type does not exist')

                # Use extensions if user has specified it in their settings.
                if upload_type == 'file' and use_extensions > 0:
                    if use_extensions == 1:
                        random_name = random_name + ext
                    elif use_extensions == 2:
                        random_name = "{}/{}".format(random_name, filename)

                # Only return JSON if it was requested by javascript.
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return {
                        'success': True,
                        'error': False,
                        'url': '/' + ('' if upload_type == 'file' else upload_type + '/') + random_name,
                        'key': 'anon' if is_anon else key,
                        'base': host,
                        'type': ext
                    }
                else:
                    response.content_type = 'text/html; charset=utf-8'
                    return host + '/' + random_name
        else:
            return functions.json_error(errors)
    else:
        return functions.json_error('Invalid key given. (can only contain letters, numbers, underscores and hyphens)')


@app.route('/api/edit/paste', method='POST')
def api_edit_paste():
    SESSION = request.environ.get('beaker.session', {})

    form = {
        'key': request.forms.get('key', False),
        'password': request.forms.get('password', False),
        'paste': request.forms.get('paste_edit_body', False),
        'id': request.forms.get('id', False),
        'commit': request.forms.get('commit', False)
    }

    is_anon = (not form['key'])

    # Generate paste name
    random_name = id_generator(random.SystemRandom().randint(4, 7))

    # Select the paste that is being edited
    paste_row = config.db.select(
        'pastes', where={'id': form['id']}, singular=True)

    # Check credentials for user if they exist, else make a new account.
    if is_anon:
        is_authed = True
        user_row = None
        user_id = 0
    else:
        user_row = config.db.select(
            'accounts', where={'key': form['key']}, singular=True)

        if user_row:
            is_authed = (user_row['password'] == form['password'])
            user_id = user_row['id']
        else:
            new_account = config.db.insert(
                'accounts', {'key': form['key'], 'password': form['password']})
            user_id = new_account.lastrowid
            is_authed = True

    if is_authed:
        # Generate a hash for the paste revision
        commit = hashlib.sha1(form['paste'].encode('utf-8')).hexdigest()[0:7]

        # Check whether to fork or just edit the paste
        is_fork = True if not user_row else (user_id != paste_row['userid'])

        # Reject long pastes
        if len(form['paste']) > 65000:
            return functions.json_error('Your paste exceeds the maximum character length of 65000')
        else:
            if paste_row and (user_id or is_anon):
                # Set credentials for an account in case they changed
                if not is_anon:
                    SESSION['key'] = form['key']
                    SESSION['password'] = form['password']
                    SESSION['id'] = user_id

                if is_fork:
                    # Insert into pastes as well as the users gallery as a fork
                    paste_id = config.db.insert(
                        'pastes', {'userid': user_id,
                                   'shorturl': random_name,
                                   'name': paste_row['name'],
                                   'lang': paste_row['lang'],
                                   'content': form['paste']}).lastrowid

                    config.db.insert(
                        'files', {'userid': user_id,
                                  'shorturl': random_name,
                                  'ext': 'paste',
                                  'original': paste_id})

                # Insert as a revision regardless of being a fork or edit
                config.db.insert(
                    'revisions', {'pasteid': paste_row['id'] if not is_fork else paste_id,
                                  'userid': user_id,
                                  'commit': commit,
                                  'message': form['commit'],
                                  'paste': form['paste'],
                                  'fork': is_fork,
                                  'parent': paste_row['id']})

                # Return data as JSON to javascript
                return {
                    'success': True,
                    'error': False,
                    'url': '/paste/{}'.format(paste_row['shorturl'] + '.' + commit if not is_fork else random_name),
                    'key': 'anon' if is_anon else form['key'],
                    'base': get_setting('directories.url')
                }
            else:
                return functions.json_error('An error has occured.')
    else:
        return functions.json_error('You are not authorized.')
