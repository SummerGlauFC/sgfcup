import os

from flask import Blueprint
from flask import current_app
from flask import render_template
from flask import send_from_directory
from flask import session
from flask import url_for
from flask_login import logout_user

from project.forms import LoginForm
from project.forms.paste import PasteForm
from project.functions import get_next_url
from project.functions import list_languages
from project.functions import redirect_next

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
    # save the next parameter in the session
    session["next"] = get_next_url()
    form = LoginForm()
    if form.validate_on_submit():
        user, is_authed = form.get_or_create_account()
        if user and is_authed:
            form.login(user)
    return render_template("login.tpl", form=form)


@blueprint.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    redirect_next(default=url_for("static.login"))


@blueprint.route("/favicon.ico")
def favicon():
    # Serve the favicon
    return send_from_directory(
        os.path.join(current_app.root_path, "static", "misc"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )
