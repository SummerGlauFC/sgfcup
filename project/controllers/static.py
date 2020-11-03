import os

from flask import render_template
from flask import send_from_directory
from flask import session

from project import app
from project.forms import LoginForm
from project.forms.paste import PasteForm
from project.functions import list_languages
from project.services.account import AccountService


@app.route("/")
def index():
    form = LoginForm()
    return render_template("index.tpl", form_login=form)


@app.route("/paste")
def paste_home():
    form = PasteForm()
    return render_template("pastebin.tpl", langs=list_languages(), form_paste=form)


@app.route("/keys")
def keys():
    # TODO: remove when account login implemented
    settings = AccountService.get_settings(session.get("id", 0))

    key = session.get("key", None)
    password = session.get("password", None)
    gallery_password = settings["gallery_password"]["value"] or None

    message = ""
    if key:
        message += f"Key: {key}"
    if password:
        message += f"<br />Password: {password}"
    if gallery_password:
        message += f"<br />Gallery view password: {gallery_password}"

    # Provide the user with their details.
    return render_template("general.tpl", title="Keys", content=message)


@app.route("/favicon.ico")
def favicon():
    # Serve the favicon
    return send_from_directory(
        os.path.join(app.root_path, "static", "misc"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )
