from typing import Optional
from typing import Union
from urllib.parse import quote

from flask import Blueprint
from flask import request
from flask_login import current_user
from flask_login import login_user

from project import functions
from project.extensions import user_settings
from project.forms import LoginForm
from project.forms import flatten_errors
from project.forms.paste import PasteEditForm
from project.forms.paste import PasteForm
from project.functions import get_host
from project.functions import get_setting
from project.services.account import AccountService
from project.services.file import FileInterface
from project.services.file import FileService
from project.services.paste import PasteInterface
from project.services.paste import PasteService
from project.services.paste import RevisionInterface

id_generator = functions.id_generator

blueprint = Blueprint("upload", __name__)


def handle_auth_or_abort(key, password):
    user, is_authed = AccountService.get_or_create_account(key, password)
    user_id = user["id"]
    if not user_id == 0:
        # Store the users credentials in the session.
        # session.permanent = True
        # session["key"] = key
        # session["password"] = password
        # session["id"] = user_id
        login_user(user, remember=True)
    if not is_authed:
        raise functions.json_error("Incorrect Key or password", status=401)
    return user_id


def submit_file(user_id) -> FileInterface:
    files = request.files.get("files")
    if not files or files.filename == "":
        raise functions.json_error("No file provided")

    file = FileService.upload(files, FileInterface(userid=user_id))
    # escape extension and original filename for URLs
    file["ext"] = quote(file["ext"])
    file["original"] = quote(file["original"])

    # Use extensions if user has specified it in their settings.
    use_extensions = user_settings.get(user_id, "ext")
    if use_extensions == 1:
        file["shorturl"] += file["ext"]
    elif use_extensions == 2:
        file["shorturl"] += "/{}".format(file["original"])

    return file


def submit_paste(user_id, paste_data=None) -> PasteInterface:
    if paste_data is None:
        form = PasteForm()
        if not form.validate():
            raise functions.json_error(
                "Error submitting paste.", errors=flatten_errors(form.errors)
            )

        paste_data = {
            "content": form.body.data,
            "name": form.name.data,
            "lang": form.lang.data,
        }

    paste_data["userid"] = user_id
    paste = PasteService.upload(PasteInterface(**paste_data))
    return paste


# File upload endpoint.
@blueprint.route("/api/upload", methods=["POST"])
@blueprint.route("/api/upload/<upload_type>", methods=["POST"])
def api_upload_file(upload_type="file"):
    if upload_type not in ["file", "paste"]:
        # The type the user provided doesn't exist.
        raise functions.json_error("This upload type does not exist")

    if not current_user.is_authenticated:
        form = LoginForm()
        key = form.key.data
        password = form.password.data
        user_id = handle_auth_or_abort(key, password)
    else:
        key = current_user["key"]
        user_id = current_user.get_id()

    is_file = upload_type == "file"

    # defaults for an impossible case
    file: Optional[Union[FileInterface, PasteInterface]] = None
    if is_file:
        file = submit_file(user_id)
    elif upload_type == "paste":
        file = submit_paste(user_id)

    if not file:
        raise functions.json_error("Failed to upload file")

    shorturl = file["shorturl"]
    ext = file["ext"] if is_file else "paste"

    host = get_host()
    path = "/" + ("" if is_file else upload_type + "/")
    return functions.json_response(
        type=ext,
        key="anon" if not user_id else key,
        base=host,
        url=path + shorturl,
        full_url=host + path + shorturl,
    )


@blueprint.route("/api/edit/paste", methods=["POST"])
def api_edit_paste():
    form = PasteEditForm()
    if not form.validate():
        raise functions.json_error(
            "Error editing paste.", errors=flatten_errors(form.errors)
        )

    form = PasteEditForm()

    if not current_user.is_authenticated:
        key = form.key.data
        password = form.password.data
        user_id = handle_auth_or_abort(key, password)
    else:
        key = current_user["key"]
        user_id = current_user.get_id()

    body = form.body.data.strip()
    editing_id = form.id.data
    editing_commit = form.commit.data
    msg = form.commit_message.data

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
