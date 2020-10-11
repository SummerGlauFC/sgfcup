import hashlib
import os
import random

from bottle import request

from project import app
from project import config
from project import functions
from project.functions import get_host
from project.functions import get_paste
from project.functions import get_paste_revision
from project.functions import get_session
from project.functions import get_setting
from project.services.account import AccountService
from project.services.file import FileInterface
from project.services.file import FileService

id_generator = functions.id_generator


def handle_auth(key, password):
    SESSION = get_session()
    user, is_authed = AccountService.get_or_create_account(key, password)
    user_id = user["id"]
    if not user_id == 0:
        # Store the users credentials in the session.
        SESSION["key"] = key
        SESSION["password"] = password
        SESSION["id"] = user_id
    if not is_authed:
        raise functions.json_error("Incorrect Key or password", status=401)
    return user_id


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

    path = os.path.join(directory, shorturl + ext)
    files.save(path)
    FileService.create(
        FileInterface(
            userid=user_id,
            shorturl=shorturl,
            ext=ext,
            original=filename,
            size=os.path.getsize(path),
        )
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
    FileService.create(
        FileInterface(
            userid=user_id,
            shorturl=shorturl,
            ext=ext,
            original=paste_row,
            size=len(body),
        )
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
    user_id = handle_auth(key, password)

    # defaults for an impossible case
    shorturl = ext = ""
    if upload_type == "file":
        shorturl, ext = submit_file(user_id)
    elif upload_type == "paste":
        shorturl, ext, _ = submit_paste(user_id)

    host = get_host()
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
    editing_id = request.forms.get("id", None)
    editing_commit = request.forms.get("commit", None)
    msg = request.forms.get("commit_message", None)

    abort_if_paste_body_error(body)

    if msg and len(msg) > 1024:
        raise functions.json_error(
            "Your commit message exceeds the maximum character length of 1024"
        )

    user_id = handle_auth(key, password)

    # Select the paste that is being edited
    base_paste = get_paste(editing_id)
    if not base_paste:
        raise functions.json_error("Paste does not exist")

    # Generate a hash for this paste revision
    commit = hashlib.sha1(body.encode("utf-8")).hexdigest()[0:7]
    shorturl = base_paste["shorturl"]
    paste_id = base_paste["id"]

    # Select the commit that is being edited
    parent_revision = None
    if editing_commit:
        base_revision = get_paste_revision(pasteid=paste_id, id=editing_commit)
        if not base_revision:
            raise functions.json_error("Commit does not exist")
        parent_revision = base_revision["id"]

    # Check whether to fork or just edit the paste
    is_fork = user_id != base_paste["userid"]
    if is_fork:
        shorturl, _, paste_id = submit_paste(
            user_id, dict(**base_paste, body=base_paste["content"])
        )
    else:
        # if the user is editing the paste, disallow it if it matches a previous commit
        commit_exists = get_paste_revision(pasteid=paste_id, commit=commit)
        if commit_exists:
            raise functions.json_error("Commit already exists")

    # Insert as a revision regardless of being a fork or edit
    config.db.insert(
        "revisions",
        {
            "pasteid": paste_id,
            "userid": user_id,
            "commit": commit,
            "message": msg,
            "paste": body,
            "fork": is_fork,
            "parent": base_paste["id"],
            "parent_revision": parent_revision,
        },
    )

    host = get_host()
    url = "/paste/{}".format(shorturl + ":" + commit)
    return functions.json_response(
        url=url,
        key="anon" if not user_id else key,
        base=get_setting("directories.url"),
        full_url=host + url,
    )
