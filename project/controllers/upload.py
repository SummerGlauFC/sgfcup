from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import hashlib
import os
import random

from bottle import request

from project import app
from project import config
from project import functions
from project.functions import get_or_create_account
from project.functions import get_setting

id_generator = functions.id_generator


def handle_auth(key, password):
    SESSION = request.environ.get("beaker.session", {})
    is_authed, user_id = get_or_create_account(key, password)
    if not user_id == 0:
        # Store the users credentials in the session.
        SESSION["key"] = key
        SESSION["password"] = password
        SESSION["id"] = user_id
    if not is_authed:
        raise functions.json_error("Incorrect Key or password", status=403)
    return is_authed, user_id


def submit_file(user_id):
    # Generated random file name
    shorturl = id_generator(random.SystemRandom().randint(4, 7))

    files = request.files.files
    if not files:
        raise functions.json_error("No file provided")

    directory = get_setting("directories.files")
    filename = files.filename
    name, ext = os.path.splitext(filename)
    if not ext:
        ext = ""

    files.save(directory + shorturl + ext)

    config.db.insert(
        "files",
        {
            "userid": user_id,
            "shorturl": shorturl,
            "ext": ext,
            "original": filename,
            "size": os.path.getsize(directory + shorturl + ext),
        },
    )

    # Use extensions if user has specified it in their settings.
    use_extensions = config.user_settings.get(user_id, "ext")
    if use_extensions == 1:
        shorturl = shorturl + ext
    elif use_extensions == 2:
        shorturl = "{}/{}".format(shorturl, filename)

    return shorturl, ext


def submit_paste(user_id, paste_data=None):
    # Generated random file name
    shorturl = id_generator(random.SystemRandom().randint(4, 7))

    if paste_data is None:
        paste_data = {
            "body": request.forms.get("paste_body", "").strip(),
            "name": request.forms.get("paste_name", shorturl),
            "lang": request.forms.get("lang", "text"),
        }

    body = paste_data["body"]
    ext = "paste"

    abort_if_paste_body_error(body)

    # insert paste to pastes table first...
    paste_entry = config.db.insert(
        "pastes",
        {
            "userid": user_id,
            "shorturl": shorturl,
            "name": paste_data["name"],
            "lang": paste_data["lang"],
            "content": body,
        },
    )

    paste_row = paste_entry.lastrowid

    # ... then add to files table
    config.db.insert(
        "files",
        {
            "userid": user_id,
            "shorturl": shorturl,
            "ext": ext,
            "original": paste_row,
            "size": len(body),
        },
    )

    return shorturl, ext, paste_row


def abort_if_paste_body_error(body):
    if not body:
        raise functions.json_error("No paste content provided")
    # Reject pastes longer than 65000 characters
    if len(body) > 65000:
        raise functions.json_error(
            "Your paste exceeds the maximum character length of 65000"
        )


# File upload endpoint.
@app.route("/api/upload", method="POST")
@app.route("/api/upload/<upload_type>", method="POST")
def api_upload_file(upload_type="file"):
    if upload_type not in ["file", "paste"]:
        # The type the user provided doesn't exist.
        raise functions.json_error("This upload type does not exist")

    # Short references
    key = request.forms.get("key", False)
    password = request.forms.get("password", False)
    is_authed, user_id = handle_auth(key, password)

    # Decide whether to return a https URL or not
    host = "{}://{}".format(
        "https" if get_setting("ssl") else "http", request.environ.get("HTTP_HOST"),
    )

    # defaults for an impossible case
    shorturl = ext = ""
    if upload_type == "file":
        shorturl, ext = submit_file(user_id)
    elif upload_type == "paste":
        shorturl, ext, _ = submit_paste(user_id)

    path = "/" + ("" if upload_type == "file" else upload_type + "/")

    return functions.json_response(
        type=ext,
        key="anon" if not user_id else key,
        base=host,
        url=path + shorturl,
        full_url=host + path + shorturl,
    )


@app.route("/api/edit/paste", method="POST")
def api_edit_paste():
    key = request.forms.get("key", False)
    password = request.forms.get("password", False)
    body = request.forms.get("paste_edit_body", "").strip()
    editing_id = request.forms.get("id", False)
    commit_msg = request.forms.get("commit", False)

    abort_if_paste_body_error(body)

    is_authed, user_id = handle_auth(key, password)

    # Select the paste that is being edited
    paste_row = config.db.select("pastes", where={"id": editing_id}, singular=True)
    if not paste_row:
        raise functions.json_error("Paste does not exist")

    # Generate a hash for the paste revision
    commit = hashlib.sha1(body.encode("utf-8")).hexdigest()[0:7]

    shorturl = id_generator(random.SystemRandom().randint(4, 7))
    paste_id = paste_row["id"]

    # Check whether to fork or just edit the paste
    is_fork = user_id != paste_row["userid"]
    if is_fork:
        paste_data = dict(**paste_row, body=body)
        shorturl, _, paste_id = submit_paste(user_id, paste_data)

    # Insert as a revision regardless of being a fork or edit
    config.db.insert(
        "revisions",
        {
            "pasteid": paste_id,
            "userid": user_id,
            "commit": commit,
            "message": commit_msg,
            "paste": body,
            "fork": is_fork,
            "parent": paste_row["id"],
        },
    )

    return functions.json_response(
        url="/paste/{}".format(
            paste_row["shorturl"] + "." + commit if not is_fork else shorturl
        ),
        key="anon" if not user_id else key,
        base=get_setting("directories.url"),
    )
