import ghdiff
from flask import Blueprint
from flask import Response
from flask import abort
from flask import make_response
from flask import redirect
from flask import render_template
from flask_login import current_user

from project import db
from project import functions
from project.constants import FileType
from project.constants import PasteAction
from project.forms.paste import PasteEditForm
from project.services.file import FileService
from project.services.paste import PasteService
from project.services.paste import RevisionInterface

blueprint = Blueprint("view", __name__)


@blueprint.route("/paste/<url>")
@blueprint.route("/paste/<url>/<flag>")
@blueprint.route("/paste/<url>:<commit>")
@blueprint.route("/paste/<url>:<commit>/<flag>")
def paste_view(url, commit=None, flag=None):
    # TODO: simplify paste view controller

    flag = PasteAction.get(flag)
    flag_path = "/" + flag.value if flag.value else ""

    # redirect to the base url if commit is "base"
    if commit == "base":
        return redirect(f"/paste/{url}{flag_path}")

    # Disable the ability to use diff on the base commit only
    if not commit and flag == PasteAction.DIFF:
        return redirect(f"/paste/{url}")

    # Select the paste from `files`
    file = FileService.get_by_url(url)
    if not file:
        abort(404)

    paste = PasteService.get_by_id(file["original"])
    if not paste:
        # Paste exists in files table but not in pastes table... remove it.
        db.delete("files", {"id": file["id"]})
        abort(404)

    # redirect user to the latest revision if commit is "latest"
    if commit == "latest":
        revision = PasteService.get_latest_revision(paste)
        if revision:
            # add latest commit hash to the URL
            url = f"{url}:{revision['commit']}"
        return redirect(f"/paste/{url}{flag_path}")

    # Get revisions for specified paste
    revisions = PasteService.get_revisions(RevisionInterface(pasteid=paste["id"]))
    commits = ["base"]
    if revisions:
        first_revision = revisions[0]
        if not commit:
            # user navigated to a forked paste, without specifying a commit
            # so redirect to the first commit for the paste.
            if first_revision["fork"]:
                redirect_commit = first_revision["commit"]
                return redirect(f"/paste/{url}:{redirect_commit}{flag_path}")

        is_fork = first_revision["fork"]
        # add the dummy base revision to the revision list
        if not is_fork:
            revisions = (RevisionInterface(commit="base"), *revisions)
        # list all available commits
        commits = [row["commit"] for row in revisions]
    else:
        revisions = []

    # commit provided but is not valid
    if commit and commit not in commits:
        abort(404, "Commit does not exist.")

    # If a commit is provided, get the revision row for that commit
    revision = next(filter(lambda rev: rev["commit"] == commit, revisions), None)

    # Add a hit to the paste file
    # Safe to count paste as viewed here since no errors occur after this point
    FileService.increment_hits(file["id"])

    # save the original paste text before we transform it
    raw_paste = revision["paste"] if revision and commit else paste["content"]
    paste["content"] = raw_paste

    # If the user provided the raw flag, skip all HTML rendering
    if flag == PasteAction.RAW:
        response: Response = make_response(raw_paste)
        response.headers.set("Content-Type", "text/plain", charset="utf-8")
        return response

    lang = paste["lang"]
    # show paste shorturl if no name
    title = f'Paste: {paste["name"] or url}'

    # paste content inc. highlighting or diff view
    content = None

    # Check if to make a diff or not,
    # depending on if the revision exists
    if revision:
        parent, parent_commit, parent_content = PasteService.get_parent(revision)
        # diff with parent paste
        if flag == PasteAction.DIFF:
            content = ghdiff.diff(parent_content, revision["paste"], css=False)
        # store URL to parent paste/revision
        revision["parent_url"] = parent["shorturl"] + (
            ":" + parent_commit if parent_commit else ""
        )
        # show commit hash in title
        title += f' [{revision["commit"]}]'

    # highlight the paste if not a diff
    if not content:
        content = functions.highlight_code(paste["content"], lang)

    # Decide whether the viewer owns this file (for forking or editing)
    # anon is always a fork
    is_owner = paste["userid"] != 0 and paste["userid"] == current_user.get_id()

    # Get the styles for syntax highlighting
    css = functions.highlight_code_css()

    # paginate the commits for a post
    pagination = functions.Pagination(
        commits.index(commit or "base") + 1, 1, len(commits), data=revisions
    )

    form_edit = PasteEditForm()
    # set edit data
    form_edit.body.data = raw_paste
    form_edit.id.data = paste["id"]
    if revision:
        form_edit.commit.data = revision["id"]

    # Provide the template with a mass of variables
    return render_template(
        "paste.tpl",
        paste=dict(
            id=paste["id"],
            raw=paste["content"],
            content=content,
            lang=lang,
            length=len(raw_paste),
            lines=len(raw_paste.split("\n")),
            own=is_owner,
            url=url,
            # add 1 hit as incrementing does not update the local value
            hits=file["hits"] + 1,
        ),
        title=title,
        css=css,
        revision=revision,
        pagination=pagination,
        flag=flag,
        form=form_edit,
    )


@blueprint.route("/<url>")
@blueprint.route("/<url>.<ext>")
@blueprint.route("/<url>/<filename>")
@blueprint.route("/<url>/<filename>.<ext>")
def image_view(url, filename=None, ext=None, file=None, update_hits=True):
    # Use passed results if provided (e.g. by thumbnailer)
    if not file:
        # Check if the requested file exists
        file = FileService.get_by_url(url)
        if not file:
            abort(404, "File not found.")

    # If the file is a paste, redirect to the pastebin
    if file["ext"] == "paste" or file["type"] == FileType.PASTE:
        return redirect(f"/paste/{url}")

    FileService.abort_if_invalid_url(file, filename, ext)

    # Add a hit to the file
    if update_hits:
        FileService.increment_hits(file["id"])

    return FileService.serve_file(file)


@blueprint.route("/api/thumb/<url>")
@blueprint.route("/api/thumb/<url>.<ext>")
@blueprint.route("/api/thumb/<url>/<filename>")
@blueprint.route("/api/thumb/<url>/<filename>.<ext>")
def thumbnail(url, filename=None, ext=None):
    # Select the full file from the database
    file = FileService.get_by_url(url)
    if not file:
        abort(404, "File not found.")

    FileService.abort_if_invalid_url(file, filename, ext)

    thumb = FileService.get_or_create_thumbnail(file)
    if thumb:
        return thumb

    # no thumb was generated, just return the actual image instead
    return image_view(url, filename, ext, file=file, update_hits=False)
