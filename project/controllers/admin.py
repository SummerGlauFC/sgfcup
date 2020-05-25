from __future__ import absolute_import, division, print_function

import os

from bottle import jinja2_template as template
from bottle import redirect, request
from project import app, config, functions
from project.functions import get_setting

# Set up short references to common variables.
db = config.db
Settings = config.Settings


def auth_session(fn):
    def check_session(**kwargs):
        SESSION = request.environ.get("beaker.session", {})

        if SESSION.get("admin"):
            return fn(**kwargs)

        redirect("/admin/login")

    return check_session


@app.get("/admin", apply=[auth_session])
def route():
    return template("admin")  # User is authed, continue to admin page


@app.post("/admin/deletehits", apply=[auth_session])
def delete_hits():
    # Short references to commonly used data
    key = (request.forms.get("key"),)
    hit_threshold = (request.forms.get("hit_threshold"),)
    all_keys = request.forms.get("all_keys", 0)

    # If admin has selected to delete from all keys
    if all_keys:
        # Select all files, where hits <= threshold.
        delete_queue = db.fetchall(
            "SELECT * FROM `files` WHERE `hits` <= %s", [hit_threshold]
        )
    else:
        # Select files from a user, where hits <= threshold
        user_id = functions.get_userid(key)
        delete_queue = db.fetchall(
            "SELECT * FROM `files` WHERE `userid` = %s AND `hits` <= %s",
            [user_id, hit_threshold],
        )

    size = 0  # total size tally
    items_deleted = 0  # items deleted tally

    if delete_queue:
        for item in delete_queue:
            # Check if item is a physical file
            if not item["ext"] == "paste":
                try:
                    size += os.stat(
                        get_setting("directories.files")
                        + item["shorturl"]
                        + item["ext"]
                    ).st_size

                    os.remove(
                        get_setting("directories.files")
                        + item["shorturl"]
                        + item["ext"]
                    )

                    items_deleted += 1
                except:
                    # 'gracefully' handle any exceptions
                    print("file does not exist:", item["shorturl"])
            else:
                db.delete("pastes", {"id": item["original"]})

        # Actually remove rows now.
        if all_keys:
            db.execute("DELETE FROM `files` WHERE `hits` <= %s", [hit_threshold])
        else:
            db.execute(
                "DELETE FROM `files` WHERE `userid` = %s and `hits` <= %s",
                [user_id, hit_threshold],
            )

        return f"{items_deleted} items deleted. {functions.sizeof_fmt(size)} of disk space saved."
    else:
        return "nothing to delete."


@app.get("/admin/login")
def login():
    # Admin login template
    return template("admin_login.tpl")


@app.post("/admin/login")
def do_login():
    SESSION = request.environ.get("beaker.session", {})

    user = request.forms.get("key")
    password = request.forms.get("password")

    admin_dict = get_setting("admin")

    if admin_dict.get(user, None) == password:
        # Allow for a persistent login
        SESSION["admin"] = True
        redirect("/admin")

    # If user provided incorrect details, just redirect back to login page
    redirect("/admin/login")
