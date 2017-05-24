from project import app, functions, config
from bottle import request, response, redirect
from bottle import jinja2_view as view, jinja2_template as template
import os
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
@view("gallery.tpl")
def gallery_view(user_key=None):
    SESSION = request.environ.get('beaker.session', {})

    # If a user does not provide a gallery to view, redirect to their own
    if not user_key and SESSION.get('key', '') != '':
        redirect('/gallery/%s' % SESSION.get('key', ''))
    else:
        user_id = functions.get_userid(user_key)
        if user_id:
            # Check the users settings to see if they have specified
            # gallery access restrictions
            settings = config.user_settings.get_all_values(user_id)

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

            # Default values for gallery options
            defaults = {
                "sort": 0,
                "in": 0,
                "page": 1,
                "case": 0,
            }

            # This function generates a url for a given page number,
            # including all GET queries and whatnot
            def url_for_page(page):
                path = request.urlparts.path
                request.query["page"] = page
                new_query = {}
                for key, value in request.query.iteritems():
                    if key in defaults:
                        value = str(value)
                        if value.isdigit() and request.query[key] != defaults[key]:
                            new_query[key] = int(value)
                    else:
                        new_query[key] = value

                return path + '?' + urllib.urlencode(new_query)

            # shorthand assignments for oftenly used data
            page = int(request.query.get('page', defaults['page']))
            case = int(request.query.get('case', defaults['case']))
            query_in = functions.get_inrange(
                request.query.get('in'), defaults['in'], len(config.searchmodes))
            query = request.query.get('query', '')
            current_sort = functions.get_inrange(
                request.query.get('sort'), defaults['sort'], len(config.sortmodes))

            # Start organising the SQL search ability
            # maybe this should be rewritten into a reusable class?
            # NOTE: this might be hard as it depends a lot on the structure
            #       i've already established in this project
            sql_search = ''
            # Ensure case-sensitive searching with a binary conversion
            collate = ' COLLATE utf8_bin ' if case else ' '

            # oh my god building SQL like this is disgusting but
            # i don't have the effort to make it better
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

            # generate pages with a useful pagination class
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
                        paste_row = config.db.select(
                            'pastes', where={"id": row["original"]}, singular=True)

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

                        row_file["url"] = row["shorturl"]
                        row_file["ext"] = row["ext"]
                        row_file["original"] = row["original"]
                        row_file["hits"] = row["hits"]
                        row_file["size"] = functions.sizeof_fmt(row["size"])

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

            tally = config.db.fetchone('SELECT SUM(`size`) AS `total` FROM `files` WHERE `userid` = %s', [user_id])
            if tally:
                usage = functions.sizeof_fmt(float(tally['total']))
            else:
                usage = functions.sizeof_fmt(1.0)

            return {
                "info": {
                    "key": user_key,
                    "id": user_id,
                    "pages": pagination,
                    "usage": usage,
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
            }
        else:
            return functions.json_error("Specified key does not exist.")


@app.route('/gallery/auth/<user_key:re:[a-zA-Z0-9_-]+>', method="GET")
def gallery_auth_view(user_key):
    return template('gallery_auth.tpl')


@app.route('/gallery/auth/<user_key:re:[a-zA-Z0-9_-]+>', method="POST")
def gallery_auth_do(user_key):
    # Set a long cookie to grant a user access to a gallery
    max_age = (3600 * 24 * 7 * 30 *
               12) if int(request.forms.get('remember', 0)) else None
    authcode = request.forms.get('authcode')
    response.set_cookie("auth+%s" % functions.get_userid(user_key),
                        hashlib.sha1(authcode).hexdigest(), max_age=max_age, path="/")
    redirect('/gallery/%s' % user_key)


@app.route('/gallery/delete/advanced', method="GET")
@view('delete_advanced.tpl')
def gallery_delete_advanced_view():
    SESSION = request.environ.get('beaker.session', {})

    return {
        "key": SESSION.get('key', '')
    }


def delete_files(to_delete, messages):
    size = 0
    count = 0

    for row in to_delete:
        is_paste = (row["ext"] == "paste")
        size += row["size"]
        count += 1

        config.db.delete(
            'files', {"shorturl": row["shorturl"]})

        # Special treatment for pastes as they don't physically exist
        # on the disk
        if is_paste:
            config.db.delete(
                'pastes', {"id": row["original"]})
        else:
            try:
                os.remove(config.Settings["directories"]["files"]
                          + row["shorturl"] + row["ext"])
                messages.append('Removed file "%s" (%s)' %
                                (row["original"], row["shorturl"]))
            except OSError:
                messages.append('Could not delete %s' %
                                row["shorturl"])

    return (size, count, messages)


@app.route('/gallery/delete/advanced', method="POST")
def gallery_delete_advanced():
    def build_sql_parts(form):
        mapping = {
            "less": '<=',
            "greater": '>='
        }
        if (form.get("operator") in ['less', 'greater']
                and form.get("type") in ['hits', 'size']
                and form.get("key")
                and form.get("password")
                and form.get("threshold")):
            operator = mapping[form.get("operator")]
            del_type = form.get("type")
            key = form.get("key")
            password = form.get("password")
            threshold = form.get('threshold')
        else:
            return False

        return {"table": 'files',
                "operator": operator,
                "threshold": threshold,
                "type": del_type,
                "key": key,
                "password": password}

    parts = build_sql_parts(request.forms)
    user = None

    if parts:
        user = config.db.select('accounts', where={"key": parts[
                                'key'], "password": parts['password']}, singular=True)

    size = 0
    count = 0
    messages = []

    if user and parts:
        user_id = user["id"]
        sql = "SELECT * FROM `{table}` WHERE `userid` = %s AND `{type}` {operator} %s".format(
            **parts)
        files = config.db.fetchall(sql, [user_id, parts["threshold"]])
        size, count, messages = delete_files(files, messages)

        messages.append("{0} items deleted. {1} of disk space saved.".format(
            count, functions.sizeof_fmt(size)))
    else:
        return 'Not authed or malformed request.'

    return template('delete.tpl', messages=messages, key=parts['key'])


@app.route('/gallery/delete', method="POST")
def gallery_delete():
    files_to_delete = request.forms.getall('delete_this')
    key = request.forms.get('key')
    password = request.forms.get('password')

    del_type = request.forms.get('type')

    messages = []

    if del_type in ["Delete Selected", "Delete All"]:
        # Get the information for a user and check basics like
        # if the password is correct or if they've even provided files to
        # delete.
        userid = functions.get_userid(key, return_row=True)
        if userid["password"] != password:
            return template('general.tpl',
                            title='Error', content="Password is incorrect.")
        elif not files_to_delete and del_type == "Delete Selected":
            return template('general.tpl',
                            title='Error', content="No files were provided.")

        keys_uploads = config.db.select(
            'files', where={"userid": userid["id"]})

        if del_type == "Delete Selected":
            selected_only = [row for row in keys_uploads if row[
                "shorturl"] in files_to_delete]
            size, count, messages = delete_files(selected_only, messages)
        elif del_type == "Delete All":
            size, count, messages = delete_files(keys_uploads, messages)

        messages.append("{0} items deleted. {1} of disk space saved.".format(
            count, functions.sizeof_fmt(size)))

        # Optimize the tables after delete operations
        config.db.execute('OPTIMIZE TABLE `files`')
        config.db.execute('OPTIMIZE TABLE `pastes`')

        return template('delete.tpl', messages=messages, key=key)
    else:
        return template('general.tpl',
                        title='Error', content="That is not a valid delete type.")
