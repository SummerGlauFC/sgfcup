from bottle import jinja2_view as view
from bottle import request
from bottle import static_file

from project import app
from project import config
from project import functions


# File to serve (mostly) static files, like the upload pages, the
# user info page, the favicon and all stylesheets
# (provided their HTTP server doesn't serve the stylesheets/favicon)


def key_password_return(SESSION):
    SESSION = request.environ.get("beaker.session", {})

    # Check if the user has got their key and password stored, else
    # generate a mostly secure key for them.
    if SESSION.get("id"):
        return {"key": SESSION.get("key"), "password": SESSION.get("password")}

    return {"key": functions.id_generator(15), "password": functions.id_generator(15)}


@app.route("/")
@view("index.tpl")
def index():
    return key_password_return(request.environ.get("beaker.session"))


@app.get("/paste")
@view("pastebin.tpl")
def paste_home():
    return dict(
        langs=functions.list_languages(),
        **key_password_return(request.environ.get("beaker.session")),
    )


@app.route("/keys")
@view("general.tpl")
def keys():
    SESSION = request.environ.get("beaker.session", {})

    settings = config.user_settings.get_all_values(SESSION.get("id", 0))

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
    return {"title": "Keys", "message": message}


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
