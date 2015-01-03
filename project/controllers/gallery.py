from project import app, functions, config
from bottle import static_file, request, response, redirect
from bottle import jinja2_view as view, jinja2_template as template
import os
import datetime
import urllib
import functools
import hashlib


@app.route('/redirect/gallery/<user_key>')
def gallery_redirect(user_key=None):
    if not user_key:
        redirect('/')
    else:
        redirect('/gallery/%s' % user_key)


@app.route('/gallery/', method="GET")
@app.route('/gallery/<user_key>', method="GET")
def gallery_view(user_key=None):
    SESSION = request.environ.get('beaker.session')

    if not user_key:
        redirect('/redirect/gallery/%s' % SESSION.get('key', ''))
    else:
        user_id = functions.get_userid(user_key)
        if user_id:
            settings = config.user_settings.get_all_values(user_id)

            print settings

            if settings["block"]["value"] and settings["gallery_password"]["value"]:
                auth_cookie = request.get_cookie("auth+%s" % user_id)
                if not auth_cookie:
                    redirect('/gallery/auth/' + user_key)
                else:
                    hex_pass = hashlib.sha1(
                        settings["gallery_password"]["value"]).hexdigest()

                    if not hex_pass == auth_cookie:
                        redirect('/gallery/auth/' + user_key)

            files = []
            error = ''
            page_error = False

            defaults = {
                "sort": 0,
                "in": 0,
                "page": 1,
                "case": 0
            }

            def url_for_page(page):
                get_query = request.query
                path = request.urlparts.path
                get_query["page"] = page
                new_query = {}
                for key, value in get_query.iteritems():
                    if key in defaults:
                        value = str(value)
                        if value.isdigit() and get_query[key] != defaults[key]:
                            new_query[key] = int(value)
                    else:
                        new_query[key] = value

                return path + '?' + urllib.urlencode(new_query)

            page = int(request.query.get('page', defaults['page']))
            case = int(request.query.get('case', defaults['case']))
            query_in = functions.get_inrange(
                request.query.get('in'), defaults['in'], len(config.searchmodes))
            query = request.query.get('query', '')
            current_sort = functions.get_inrange(
                request.query.get('sort'), defaults['sort'], len(config.sortmodes))

            sql_search = ''
            collate = ' COLLATE utf8_bin ' if case else ' '
            if query:
                sql_search = '`%s`%sLIKE %%s AND' % (
                    config.searchmodes[query_in][1], collate)

            sort_array = config.sortmodes[current_sort]
            sql_query = 'SELECT * FROM `files` WHERE %s `userid` = %%s ORDER BY `%s` %s LIMIT {}' % (
                sql_search, sort_array[1], sort_array[2])

            format_list = []
            if query:
                format_list.append("%" + query + "%")
            format_list.append(user_id)

            total_entries = config.db.fetchone(
                'SELECT COUNT(`userid`) AS total FROM `files` WHERE ' + (sql_search if query else '') + '`userid` = %s', format_list)['total']

            pagination = functions.Pagination(page, 30, total_entries)

            results = config.db.fetchall(
                sql_query.format(pagination.limit), format_list)

            if page > pagination.pages:
                if pagination.pages == 0:
                    error += "There were no results for this search query."
                else:
                    error += "This page does not exist. "

            if results and error == '':
                for row in results:
                    row_file = {}

                    if row["ext"] == "paste":
                        paste_row = config.db.fetchone(
                            'SELECT * FROM `pastes` WHERE `id` = %s', [row["original"]])

                        row_file["type"] = 2
                        row_file["url"] = row["shorturl"]
                        row_file["content"] = paste_row["content"]
                        row_file["hits"] = row["hits"]
                        row_file["name"] = paste_row["name"] or row["shorturl"]
                        row_file["size"] = len(
                            paste_row["content"].split('\n'))

                        row_file["time"] = {
                            "epoch": row["date"].strftime('%s'),
                            "timestamp": row["date"].strftime('%d/%m/%Y @ %H:%M:%S')
                        }
                    else:
                        full_file_path = config.Settings["directories"][
                            "files"] + row["shorturl"] + row["ext"]

                        image = functions.is_image(full_file_path)
                        try:
                            file_stats = os.stat(full_file_path)
                            row_file["size"] = functions.sizeof_fmt(
                                file_stats.st_size)
                        except:
                            pass

                        row_file["url"] = row["shorturl"]
                        row_file["ext"] = row["ext"]
                        row_file["original"] = row["original"]
                        row_file["hits"] = row["hits"]

                        row_file["time"] = {
                            "epoch": row["date"].strftime('%s'),
                            "timestamp": row["date"].strftime('%d/%m/%Y @ %H:%M:%S')
                        }

                        if image:
                            row_file["type"] = 0
                            row_file["resolution"] = image.size
                        else:
                            row_file["type"] = 1

                    files.append(row_file)

            return template("new_gallery.tpl" if settings["gallery_style"]["value"] else "gallery.tpl", {
                "info": {
                    "key": user_key,
                    "id": user_id,
                    "pages": pagination,
                    "file_types": config.file_types,
                    "sort": {
                        "current": current_sort,
                        "list": config.sortmodes
                    },
                    "search": {
                        "query": query,
                        "in": query_in,
                        "modes": config.searchmodes,
                        "case": case
                    },
                    "files": files,
                    "pjax": request.headers.get('X-AJAX', 'false') == 'true',
                    "show_ext": settings["ext"]["value"]
                },
                "url_for_page": url_for_page,
                "error": error if error else False,
                "types": config.file_type,
                "hl": functools.partial(functions.hl, search=query)
            })
        else:
            return template("gallery.tpl", {"error": "Specified key does not exist."})


@app.route('/gallery/auth/<user_key:re:[a-zA-Z0-9_-]+>', method="GET")
def gallery_auth_view(user_key):
    return template('gallery_auth.tpl')


@app.route('/gallery/auth/<user_key:re:[a-zA-Z0-9_-]+>', method="POST")
def gallery_auth_do(user_key):
    max_age = (3600 * 24 * 7 * 30 *
               12) if int(request.forms.get('remember', 0)) else None
    authcode = request.forms.get('authcode')
    response.set_cookie("auth+%s" % functions.get_userid(user_key),
                        hashlib.sha1(authcode).hexdigest(), max_age=max_age, path="/")
    redirect('/gallery/%s' % user_key)


@app.route('/gallery/delete', method="POST")
def gallery_delete():
    files_to_delete = request.forms.getall('delete_this')
    key = request.forms.get('key')
    password = request.forms.get('password')

    messages = []

    userid = functions.get_userid(key, return_row=True)
    if userid["password"] != password:
        return template('general.tpl',
                        title='Error', content="Password is incorrect.")
    elif not files_to_delete:
        return template('general.tpl',
                        title='Error', content="No files were provided.")

    keys_uploads = config.db.fetchall(
        'SELECT * FROM `files` WHERE `userid` = %s', [userid["id"]])

    file_rows = {}
    for row in keys_uploads:
        file_rows[row["shorturl"]] = row

    for short_url in files_to_delete:
        if short_url not in file_rows:
            messages.append(
                'File "%s" does not belong to this user or does not exist.' %
                short_url)
        else:
            file_row = file_rows[short_url]
            is_paste = (file_row["ext"] == "paste")

            delete_query = config.db.execute(
                "DELETE FROM `files` WHERE `shorturl` = %s", [short_url])

            if is_paste:
                config.db.execute(
                    'DELETE FROM `pastes` WHERE `id` = %s', [file_row["original"]])
            else:
                try:
                    os.remove(config.Settings["directories"]["files"]
                              + short_url + file_row["ext"])
                    messages.append('Removed file "%s" (%s)' %
                                    (file_row["original"], short_url))
                except OSError:
                    messages.append('Could not delete %s' % short_url)

    config.db.execute('OPTIMIZE TABLE `files`')
    config.db.execute('OPTIMIZE TABLE `pastes`')

    return template('delete.tpl', messages=messages, key=key)
