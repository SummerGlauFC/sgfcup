from __future__ import division, print_function, absolute_import
from project import app, config, functions
from bottle import request, abort, redirect, response
from bottle import static_file as bottle_static_file
from bottle import jinja2_template as template
import os
from PIL import Image, ImageOps
import magic
import ghdiff

# courtesy of Humphrey@stackoverflow
# https://stackoverflow.com/a/35859141
def remove_transparency(im, bg_colour=(255, 255, 255)):
    # Only process if image has transparency
    # (http://stackoverflow.com/a/1963146)
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):

        # Need to convert to RGBA if LA format due to a bug in PIL
        # (http://stackoverflow.com/a/1963146)
        alpha = im.convert('RGBA').split()[-1]

        background = Image.new("RGB", im.size, bg_colour)
        background.paste(im, mask=alpha) # 3 is the alpha channel
        return background

    else:
        return im


def static_file(path, root, filename=False):
    file_path = root + path
    mime = magic.from_file(file_path, mime=True)

    def set_file_info(resp):
        resp.set_header('Content-Type', mime)
        if filename:
            resp.set_header('Content-Disposition',
                            'inline; filename="{0}"'.format(filename))
        return resp

    set_file_info(response)

    # Use the sendfile built into nginx if it's available
    if config.Settings["use_nginx_sendfile"]:
        folder = 't' if root is config.Settings[
            'directories']['thumbs'] else 'p'

        response.set_header('X-Accel-Redirect',
                            '/get_image/{}/{}'.format(folder, path))

        return 'This should be handled by nginx.'
    else:
        return set_file_info(bottle_static_file(path, root=root, mimetype=mime))


@app.route('/api/thumb/<url>')
@app.route('/api/thumb/<url>.<ext>')
def api_thumb(url, ext=None, temp=False, size=(400, 400)):
    # Thumbnailer route
    # Generated for the gallery

    # Return the currently saved thumbnail if it exists
    if 'thumb_' + url + '.jpg' in os.listdir(config.Settings['directories']['thumbs']) and not temp:
        return static_file('thumb_' + url + '.jpg',
                           root=config.Settings['directories']['thumbs'])
    elif 'thumb_' + url + '.jpg' in os.listdir('/tmp') and temp:
        return static_file('thumb_' + url + '.jpg', root='/tmp/')
    else:
        # Select the full file from the database
        results = config.db.fetchone(
            'SELECT * FROM `files` WHERE BINARY `shorturl` = %s', [url])

        if results:
            # Check if extension matches the one in the database (if provided)
            if ext and ('.' + ext != results["ext"]):
                abort(404, 'File not found.')
            else:
                # Generate a 400x400 (by default) JPEG thumbnail
                base = Image.open(
                    config.Settings['directories']['files'] + results["shorturl"] + results["ext"])
                if size < base.size:
                    image_info = base.info
                    # if base.mode not in ("L", "RGBA"):
                    #     base = base.convert("RGBA")
                    base = ImageOps.fit(base, size, Image.ANTIALIAS)
                    save_dir = '/tmp/' if temp else config.Settings[
                        'directories']['thumbs']
                    base = remove_transparency(base)
                    base.save(save_dir + 'thumb_' + url + '.jpg', **image_info)
                    return static_file('thumb_' + url + '.jpg', root=save_dir)
                else:
                    return image_view(url, ext, results=results)
        else:
            abort(404, 'File not found.')


@app.route('/<url>')
@app.route('/<url>.<ext>')
def image_view(url, ext=None, results=None, update_hits=True):
    # Check if the requested file exists
    # Also, use a passed-through results if it exists.
    if not results:
        results = config.db.fetchone(
            'SELECT * FROM `files` WHERE BINARY `shorturl` = %s', [url])

    if results:
        # Check if extension matches the one in the database (if provided)
        if ext and ('.' + ext != results["ext"]):
            abort(404, 'File not found.')
        else:
            # If the file is a paste, redirect to the pastebin
            if results["ext"] == 'paste':
                redirect('/paste/%s' % url)
            else:
                # Add one hit to the file
                if update_hits:
                    config.db.execute(
                        'UPDATE `files` SET hits=hits+1 WHERE `id`=%s', [results["id"]])

                return static_file(
                    results["shorturl"] + results["ext"],
                    root=config.Settings["directories"]["files"],
                    filename=results["original"])

    abort(404, 'File not found.')


@app.route('/paste/<url>')
@app.route('/paste/<url>/<flag>')
@app.route('/paste/<url>/<flag>.<ext>')
def paste_view(url, flag=None, ext=None):
    SESSION = request.environ.get('beaker.session', {})

    # Extract the commit from the URL, if it exists.
    if '.' in url:
        url = url.split('.')
        commit = url[-1]
        url = url[0]
    else:
        commit = False

    # Select the paste from `files`
    results = config.db.fetchone(
        'SELECT * FROM `files` WHERE BINARY `shorturl` = %s', [url])

    if results:
        paste_row = config.db.select(
            'pastes', where={"id": results["original"]}, singular=True)

        if not paste_row:
            print('Deleting a paste that was not found...')
            # config.db.execute(
            #     "DELETE FROM `files` WHERE `id` = %s", [results['id']])
            config.db.delete('files', {"id": results['id']}, singular=True)
            abort(404, 'File not found.')

        # Select every revision for specified paste
        revisions_rows = config.db.select(
            'revisions', where={"pasteid": paste_row["id"], "fork": 0})

        # Add a hit to the paste
        config.db.execute(
            'UPDATE `files` SET hits=hits+1 WHERE `id`=%s', [results["id"]])

        # Decide whether the viewer owns this file (for forking or editing)
        is_owner = (paste_row["userid"] == SESSION.get("id", 0))

        # If a commit is provided, get the row for that revision
        if commit:
            revisions_row = config.db.select(
                'revisions', where={"commit": commit}, singular=True)
        else:
            revisions_row = None

        # Add the base commit in by default
        commits = ['base']

        # Append every commit which exists
        if revisions_rows:
            for row in revisions_rows:
                commits.append(row["commit"])

        # Check if the commit exists in the commits list
        if commit in commits:
            current_commit = commits.index(commit)
            current_commit = commits[
                current_commit - 1 if current_commit - 1 >= 0 else 0]
        else:
            current_commit = commits[0]

        # Disable the ability to use diff on the base commit only
        if current_commit == "base" and commit == "" and flag == "diff":
            flag = ""

        # Function to get the previous commit from the database for diffs
        def previous_commit():
            if current_commit != 'base':
                return config.db.select('revisions', where={"commit": current_commit}, singular=True)["paste"]
            else:
                return config.db.select('pastes', where={"id": paste_row["id"]}, singular=True)["content"]

        # If the user provided the raw flag, skip all HTML rendering
        if flag == "raw":
            response.content_type = 'text/plain; charset=utf-8'
            return revisions_row["paste"] if commit else paste_row["content"]
        else:
            revision = {}

            # Check if the paste has a name, and show the name if it does.
            if paste_row["name"]:
                title = 'Paste "%s" (%s)' % (paste_row["name"], url)
            else:
                title = 'Paste %s' % url

            lang = paste_row['lang']

            # Check if to make a diff or not,
            # depending on if the revision exists
            if revisions_row:
                if flag == "diff":
                    prev_commit = previous_commit()

                    # Render the diff without CSS, so I can edit it easier
                    paste_row["content"] = ghdiff.diff(
                        prev_commit, revisions_row["paste"], css=False)
                    lang = "diff"
                else:
                    paste_row["content"] = revisions_row["paste"]

                revision = revisions_row

                # Add the parent pastes URL to the revision's data.
                revision["parent_url"] = config.db.select(
                    'pastes', where={"id": revision["parent"]}, singular=True)["shorturl"]

                title += " (revision %s)" % revision["commit"]

            # Decide whether to wrap the response in an extra element
            use_wrapper = False if flag == "diff" and commit in commits else True

            if not use_wrapper:
                content = paste_row["content"]
            else:
                content = functions.highlight(
                    paste_row["content"], lang)

            # Get meta data about the pastes
            length = len(paste_row["content"])
            lines = len(paste_row["content"].split('\n'))
            hits = results["hits"]

            # Get the styles for syntax highlighting
            css = functions.css()

            # Generate a key and password for the edit form
            if SESSION.get('id'):
                key = SESSION.get('key')
                password = SESSION.get('password')
            else:
                key = functions.id_generator(15)
                password = functions.id_generator(15)

            # Decide if the paste should be in edit/fork mode or not
            edit = (flag == "edit")

            # Provide the template with a mass of variables
            return template('paste', title=title, content=content, css=css,
                            url=url, lang=lang, length=length,
                            hits=hits, lines=lines, edit=edit,
                            raw_paste=paste_row["content"], is_owner=is_owner,
                            key=key, password=password, id=paste_row["id"],
                            revisions=revisions_rows, revision=revision,
                            flag=flag, _commit=commit, commits=commits,
                            use_wrapper=use_wrapper)
    else:
        abort(404, 'File not found.')
