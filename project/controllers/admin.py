# -*- coding: utf-8 -*-
from project import app, config, functions
from bottle import request, redirect
from bottle import jinja2_template as template
import os

db = config.db
Settings = config.Settings


def auth_session(SESSION):
    return SESSION.get("admin", False)


@app.get('/admin')
@app.get('/admin/')
def route():
    SESSION = request.environ.get('beaker.session')

    if auth_session(SESSION):
        return template("admin")
    else:
        redirect("/admin/login")


@app.post('/admin/deletehits')
def delete_hits():
    SESSION = request.environ.get('beaker.session')

    if auth_session(SESSION):
        key = request.forms.get('key'),
        hit_threshold = request.forms.get('hit_threshold'),
        all_keys = request.forms.get('all_keys', 0)

        if all_keys:
            deleteQueue = config.db.fetchall(
                'SELECT * FROM `files` WHERE `hits` <= %s', [hit_threshold])
        else:
            user_id = functions.get_userid(key)
            deleteQueue = config.db.fetchall(
                'SELECT * FROM `files` WHERE `userid` = %s AND `hits` <= %s',
                [user_id, hit_threshold])

        size = 0
        itemsDeleted = 0

        if deleteQueue:
            for item in deleteQueue:
                if not item['ext'] == 'paste':
                    try:
                        size = size + \
                            os.stat(Settings["directories"]
                                    ["files"] + item["shorturl"] + item["ext"]).st_size
                        os.remove(
                            Settings["directories"]["files"] + item["shorturl"] + item["ext"])

                        itemsDeleted += 1
                    except:
                        print 'file', item['shorturl'], 'does not exist.'
                else:
                    config.db.execute(
                        "DELETE FROM `pastes` WHERE `id` = %s",
                        [item["original"]])

            if all_keys:
                db.execute('DELETE FROM `files` WHERE `hits` <= %s',
                           [hit_threshold])
            else:
                db.execute(
                    'DELETE FROM `files` WHERE `userid` = %s and `hits` <= %s',
                    [user_id, hit_threshold])

            return "{0} items deleted. {1} of disk space saved.".format(
                itemsDeleted, functions.sizeof_fmt(size))
        else:
            return "nothing to delete."
    else:
        redirect("/admin/login")


@app.get('/admin/login')
@app.get('/admin/login/')
def login():
    return template('admin_login.tpl')


@app.post('/admin/login')
def do_login():
    SESSION = request.environ.get('beaker.session')

    user = request.forms.get('key')
    password = request.forms.get('password')

    admin_dict = config.Settings['admin']

    if user in admin_dict and admin_dict[user] == password:
        SESSION["admin"] = True
        redirect("/admin")

    redirect("/admin/login")
