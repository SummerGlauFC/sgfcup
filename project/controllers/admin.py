from functools import wraps

from flask import redirect
from flask import render_template
from flask import request
from flask import session

from project import app
from project import db
from project import functions
from project.functions import get_setting
from project.services.account import AccountService
from project.services.file import FileService


def login_required(f):
    @wraps(f)
    def check_session(*args, **kwargs):
        if not session.get("admin"):
            return redirect("/admin/login")
        return f(*args, **kwargs)

    return check_session


@app.route("/admin", methods=["GET"])
@login_required
def route():
    return render_template("admin.tpl")  # User is authed, continue to admin page


@app.route("/admin/deletehits", methods=["POST"])
@login_required
def delete_hits():
    # Short references to commonly used data
    key = request.form.get("key", None)
    hit_threshold = request.form.get("hit_threshold", -1)
    all_keys = request.form.get("all_keys", None)

    delete_queue = ()

    # If admin has selected to delete from all keys
    if all_keys:
        # Select all files, where hits <= threshold.
        delete_queue = db.fetchall(
            "SELECT * FROM `files` WHERE `hits` <= %s", [hit_threshold]
        )
    else:
        # Select files from a user, where hits <= threshold
        user = AccountService.get_by_key(key)
        if user:
            delete_queue = db.fetchall(
                "SELECT * FROM `files` WHERE `userid` = %s AND `hits` <= %s",
                [user["id"], hit_threshold],
            )

    size, count, _ = FileService.delete_batch(delete_queue)
    return f"{count} items deleted. {functions.sizeof_fmt(size)} of disk space saved."


@app.route("/admin/login", methods=["GET"])
def login():
    # Admin login template
    return render_template("admin_login.tpl")


@app.route("/admin/login", methods=["POST"])
def do_login():
    admin = get_setting("admin").get(request.forms.get("key"), None)
    if admin and admin == request.forms.get("password"):
        # Allow for a persistent login
        session["admin"] = True
        return redirect("/admin")
    # If user provided incorrect details, just redirect back to login page
    return redirect("/admin/login")
