from functools import wraps

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import session

from project import db
from project import functions
from project.forms import LoginForm
from project.forms.admin import AdminDeleteForm
from project.functions import get_setting
from project.services.account import AccountService
from project.services.file import FileService

blueprint = Blueprint("admin", __name__)


def login_required(f):
    @wraps(f)
    def check_session(*args, **kwargs):
        if session.get("admin") is not True:
            return redirect("/admin/login")
        return f(*args, **kwargs)

    return check_session


@blueprint.route("/admin", methods=["GET"])
@login_required
def route():
    form = AdminDeleteForm()
    return render_template("admin.tpl", form=form)


@blueprint.route("/admin/deletehits", methods=["POST"])
@login_required
def delete_hits():
    form = AdminDeleteForm()
    if form.validate():
        hit_threshold = form.hit_threshold.data
        delete_queue = ()

        # If admin has selected to delete from all keys
        if form.all_keys.data:
            # Select all files, where hits <= threshold.
            delete_queue = db.fetchall(
                "SELECT * FROM `files` WHERE `hits` <= %s", [hit_threshold]
            )
        else:
            # Select files from a user, where hits <= threshold
            user = AccountService.get_by_key(form.key.data)
            if user:
                delete_queue = db.fetchall(
                    "SELECT * FROM `files` WHERE `userid` = %s AND `hits` <= %s",
                    [user.get_id(), hit_threshold],
                )

        size, count, _ = FileService.delete_batch(delete_queue)
        return render_template(
            "delete.tpl",
            messages=[
                f"{count} items deleted. {functions.sizeof_fmt(size)} of disk space saved."
            ],
        )
    flash("There was an error processing your input.", "error")
    return redirect("/admin")


@blueprint.route("/admin/login", methods=["GET", "POST"])
def login():
    if session.get("admin") is True:
        # already authenticated
        return redirect("/admin")

    form = LoginForm()
    if form.validate_on_submit():
        admin = get_setting("admin").get(form.key.data, None)
        if admin and admin == form.password.data:
            # Allow for a persistent login
            session.permanent = True
            session["admin"] = True
            return redirect("/admin")
        flash("There was a problem authenticating you.", "error")
    return render_template("admin_login.tpl", form=form)


@blueprint.route("/admin/logout", methods=["GET", "POST"])
def logout():
    session.pop("admin", None)
    flash("Successfully logged you out.")
    return redirect("/admin")
