from bottle import jinja2_template as template
from bottle import redirect
from bottle import request

from project import app
from project import config
from project import functions
from project.functions import get_session
from project.functions import get_setting
from project.services.account import AccountService
from project.services.file import FileService

db = config.db


def auth_session(fn):
    def check_session(**kwargs):
        SESSION = get_session()
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
    key = request.forms.get("key", None)
    hit_threshold = request.forms.get("hit_threshold", -1)
    all_keys = request.forms.get("all_keys", None)

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


@app.get("/admin/login")
def login():
    # Admin login template
    return template("admin_login.tpl")


@app.post("/admin/login")
def do_login():
    SESSION = get_session()
    admin = get_setting("admin").get(request.forms.get("key"), None)
    if admin and admin == request.forms.get("password"):
        # Allow for a persistent login
        SESSION["admin"] = True
        redirect("/admin")
    # If user provided incorrect details, just redirect back to login page
    redirect("/admin/login")
