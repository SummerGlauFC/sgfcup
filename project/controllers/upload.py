from typing import Optional
from typing import Union
from urllib.request import pathname2url

from bottle import request

from project import app
from project import config
from project import functions
from project.functions import get_host
from project.functions import get_session
from project.functions import get_setting
from project.services.account import AccountService
from project.services.file import FileInterface
from project.services.file import FileService
from project.services.paste import PasteInterface
from project.services.paste import PasteService
from project.services.paste import RevisionInterface

id_generator = functions.id_generator


def handle_auth_or_abort(key, password):
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


def submit_file(user_id) -> FileInterface:
    files = request.files.files
    if not files:
        raise functions.json_error("No file provided")

    file = FileService.upload(files, FileInterface(userid=user_id))
    # escape extension and original filename for URLs
    file["ext"] = pathname2url(file["ext"])
    file["original"] = pathname2url(file["original"])

    # Use extensions if user has specified it in their settings.
    use_extensions = config.user_settings.get(user_id, "ext")
    if use_extensions == 1:
        file["shorturl"] += file["ext"]
    elif use_extensions == 2:
        file["shorturl"] += "/{}".format(file["original"])

    return file


def submit_paste(user_id, paste_data=None) -> PasteInterface:
    if paste_data is None:
        paste_data = {
            "content": request.forms.get("paste_body", "").strip(),
            "name": request.forms.get("paste_name"),
            "lang": request.forms.get("lang", "text"),
        }

    abort_if_paste_body_error(paste_data["content"])

    paste_data["userid"] = user_id
    paste = PasteService.upload(PasteInterface(**paste_data))
    return paste


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
    user_id = handle_auth_or_abort(key, password)

    # defaults for an impossible case
    file: Optional[Union[FileInterface, PasteInterface]] = None
    if upload_type == "file":
        file = submit_file(user_id)
    elif upload_type == "paste":
        file = submit_paste(user_id)

    if not file:
        return functions.json_error("Failed to upload file")

    shorturl = file["shorturl"]
    ext = file["ext"] if upload_type == "file" else "paste"

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

    user_id = handle_auth_or_abort(key, password)

    # Select the paste that is being edited
    base_paste = PasteService.get_by_id(editing_id)
    if not base_paste:
        raise functions.json_error("Paste does not exist")

    shorturl = base_paste["shorturl"]
    paste_id = base_paste["id"]

    # Generate a hash for this paste revision
    commit = PasteService.get_commit_hash(body)

    # Select the commit that is being edited
    parent_revision = None
    if editing_commit:
        base_revision = PasteService.get_revision(
            RevisionInterface(pasteid=paste_id, id=editing_commit)
        )
        if not base_revision:
            raise functions.json_error("Commit does not exist")
        parent_revision = base_revision["id"]

    # Check whether to fork or just edit the paste
    is_fork = user_id != base_paste["userid"]
    if is_fork:
        paste = submit_paste(user_id, base_paste)
        shorturl = paste["shorturl"]
        paste_id = paste["id"]
    else:
        # if the user is editing the paste, disallow it if it matches a previous commit
        commit_exists = PasteService.get_revision(
            RevisionInterface(pasteid=paste_id, commit=commit)
        )
        if commit_exists:
            raise functions.json_error("Commit already exists")

    # Insert as a revision regardless of being a fork or edit
    PasteService.create_revision(
        RevisionInterface(
            pasteid=paste_id,
            userid=user_id,
            commit=commit,
            message=msg,
            paste=body,
            fork=is_fork,
            parent=base_paste["id"],
            parent_revision=parent_revision,
        ),
    )

    host = get_host()
    url = "/paste/{}".format(shorturl + ":" + commit)
    return functions.json_response(
        url=url,
        key="anon" if not user_id else key,
        base=get_setting("directories.url"),
        full_url=host + url,
    )
