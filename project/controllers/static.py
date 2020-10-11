from bottle import jinja2_view as view
from bottle import static_file

from project import app
from project.functions import get_session
from project.functions import key_password_return
from project.functions import list_languages

# File to serve (mostly) static files, like the upload pages, the
# user info page, the favicon and all stylesheets
# (provided their HTTP server doesn't serve the stylesheets/favicon)
from project.services.account import AccountService


@app.route("/")
@view("index.tpl")
def index():
    return key_password_return(get_session())


@app.get("/paste")
@view("pastebin.tpl")
def paste_home():
    return dict(langs=list_languages(), **key_password_return(get_session()))


@app.route("/keys")
@view("general.tpl")
def keys():
    # TODO: remove when account login implemented
    SESSION = get_session()

    settings = AccountService.get_settings(SESSION.get("id", 0))

    key = SESSION.get("key", None)
    password = SESSION.get("password", None)
    gallery_password = settings["gallery_password"]["value"] or None

    message = ""
    if key:
        message += f"Key: {key}"
    if password:
        message += f"<br />Password: {password}"
    if gallery_password:
        message += f"<br />Gallery view password: {gallery_password}"

    # Provide the user with their details.
    return {"title": "Keys", "content": message}


@app.route("/favicon.ico")
def favicon():
    # Serve the favicon
    return static_file("favicon.ico", root="project/static/misc")


@app.route("/static/<filepath:path>")
def server_static(filepath):
    # Serve css and flush the cache when serving it with bottle.
    response = static_file(filepath, root="project/static")
    response.set_header("Cache-Control", "no-cache")
    return response
