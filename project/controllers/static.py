import os

from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import render_template
from flask import send_from_directory
from flask import url_for
from flask_login import login_user
from flask_login import logout_user

from project.forms import LoginForm
from project.forms.paste import PasteForm
from project.functions import get_next_url
from project.functions import list_languages
from project.functions import safe_redirect
from project.services.account import AccountService

blueprint = Blueprint("static", __name__)


@blueprint.route("/")
def index():
    return render_template("index.tpl")


@blueprint.route("/paste")
def paste_home():
    form = PasteForm()
    return render_template("pastebin.tpl", langs=list_languages(), form_paste=form)


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        key = form.key.data
        password = form.password.data
        user, is_authed = AccountService.get_or_create_account(key, password)
        if not user or not is_authed:
            form.key.errors.append("Key or password is incorrect")
        else:
            login_user(user)
            next_url = get_next_url()
            if safe_redirect(next_url):
                return redirect(next_url or url_for("static.index"))
    return render_template("login.tpl", form=form)


@blueprint.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    # get next param from args, then form, then session.
    # TODO: set next in session.
    next_url = get_next_url()
    if safe_redirect(next_url):
        return redirect(next_url or url_for("static.index"))
    return redirect(url_for("static.login"))


@blueprint.route("/favicon.ico")
def favicon():
    # Serve the favicon
    return send_from_directory(
        os.path.join(current_app.root_path, "static", "misc"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )
