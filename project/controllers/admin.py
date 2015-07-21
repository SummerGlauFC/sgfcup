# -*- coding: utf-8 -*-
from project import app, config, functions
from bottle import request, redirect
from bottle import jinja2_template as template
import os

# Set up short references to common variables.
db = config.db
Settings = config.Settings


def auth_session(fn):
    def check_session(**kwargs):
        SESSION = request.environ.get('beaker.session', {})

        if SESSION.get("admin", False):
            return fn(**kwargs)
        else:
            redirect("/admin/login")

    return check_session


@app.get('/admin', apply=[auth_session])
def route():
    return template("admin")  # User is authed, continue to admin page


@app.post('/admin/deletehits', apply=[auth_session])
def delete_hits():
    # Short references to commonly used data
    key = request.forms.get('key'),
    hit_threshold = request.forms.get('hit_threshold'),
    all_keys = request.forms.get('all_keys', 0)

    # If admin has selected to delete from all keys
    if all_keys:
        # Select all files, where hits <= threshold.
        deleteQueue = config.db.fetchall(
            'SELECT * FROM `files` WHERE `hits` <= %s', [hit_threshold])
    else:
        # Select files from a user, where hits <= threshold
        user_id = functions.get_userid(key)
        deleteQueue = config.db.fetchall(
            'SELECT * FROM `files` WHERE `userid` = %s AND `hits` <= %s',
            [user_id, hit_threshold])

    size = 0  # total size tally
    itemsDeleted = 0  # items deleted tally

    if deleteQueue:
        for item in deleteQueue:
            # Check if item is a physical file
            if not item['ext'] == 'paste':
                try:
                    # Obtain file size and add to tally
                    size += os.stat(Settings["directories"]["files"]
                                    + item["shorturl"] + item["ext"]).st_size

                    # Physically(?) remove the file
                    os.remove(
                        Settings["directories"]["files"] + item["shorturl"] + item["ext"])

                    itemsDeleted += 1
                except:
                    # "gracefully" handle any exceptions
                    print 'file', item['shorturl'], 'does not exist.'
            else:
                # Just remove the paste from the database
                config.db.execute(
                    "DELETE FROM `pastes` WHERE `id` = %s",
                    [item["original"]])

        # Actually remove rows now.
        if all_keys:
            db.execute('DELETE FROM `files` WHERE `hits` <= %s',
                       [hit_threshold])
        else:
            db.execute(
                'DELETE FROM `files` WHERE `userid` = %s and `hits` <= %s',
                [user_id, hit_threshold])

        # return the tallys.
        return "{0} items deleted. {1} of disk space saved.".format(
            itemsDeleted, functions.sizeof_fmt(size))
    else:
        return "nothing to delete."


@app.get('/admin/login')
def login():
    # Admin login template
    return template('admin_login.tpl')


@app.post('/admin/login')
def do_login():
    SESSION = request.environ.get('beaker.session', {})

    user = request.forms.get('key')
    password = request.forms.get('password')

    admin_dict = config.Settings['admin']

    if user in admin_dict and admin_dict[user] == password:
        # Allow for a persistent login
        SESSION["admin"] = True
        redirect("/admin")

    # If user provided incorrect details, just redirect back to login page
    redirect("/admin/login")
