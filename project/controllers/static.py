import os

from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import url_for
from flask_login import login_user
from flask_login import logout_user

from project.forms import LoginForm
from project.forms.paste import PasteForm
from project.functions import list_languages
from project.functions import safe_redirect
from project.services.account import AccountService

blueprint = Blueprint("static", __name__)


@blueprint.route("/")
def index():
    form = LoginForm()
    return render_template("index.tpl", form_login=form)


@blueprint.route("/paste")
def paste_home():
    form = PasteForm()
    return render_template("pastebin.tpl", langs=list_languages(), form_paste=form)


@blueprint.route("/login", methods=["GET"])
def login():
    hide_cleared = request.args.get("hide_clear", None) is not None
    return render_template("login.tpl", form=LoginForm(), show_cleared=not hide_cleared)


@blueprint.route("/login", methods=["POST"])
def login_post():
    form = LoginForm()
    if form.key.data and form.validate():
        key = form.key.data
        password = form.password.data
        user, is_authed = AccountService.get_or_create_account(key, password)
        if not user or not is_authed:
            form.key.errors.append("Key or password is incorrect")
        else:
            login_user(user)
    hide_cleared = request.args.get("hide_clear", None) is not None
    return render_template("login.tpl", form=form, show_cleared=not hide_cleared)


@blueprint.route("/logout", methods=["GET"])
def logout():
    logout_user()
    hide_cleared = request.args.get("hide_clear", None) is not None
    return render_template("login.tpl", form=LoginForm(), show_cleared=not hide_cleared)


@blueprint.route("/logout", methods=["POST"])
def logout_post():
    logout_user()
    next_url = request.form.get("next_url")
    if next_url and safe_redirect(next_url):
        return redirect(next_url or url_for("static.index"))
    hide_cleared = request.args.get("hide_clear", None) is not None
    return render_template("login.tpl", form=LoginForm(), show_cleared=not hide_cleared)


@blueprint.route("/favicon.ico")
def favicon():
    # Serve the favicon
    return send_from_directory(
        os.path.join(current_app.root_path, "static", "misc"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )
