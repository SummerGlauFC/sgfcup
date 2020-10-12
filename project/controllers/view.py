import ghdiff
from bottle import abort
from bottle import jinja2_template as template
from bottle import redirect
from bottle import response

from project import app
from project import config
from project import functions
from project.configdefines import PasteAction
from project.functions import get_session
from project.functions import key_password_return
from project.services.file import FileService
from project.services.paste import PasteService


@app.route("/paste/<url>")
@app.route("/paste/<url>/<flag>")
@app.route("/paste/<url>\:<commit>")
@app.route("/paste/<url>\:<commit>/<flag>")
def paste_view(url, commit=None, flag=None):
    # TODO: simplify paste view controller
    SESSION = get_session()

    # Select the paste from `files`
    file = FileService.get_by_url(url)
    if not file:
        abort(404, "File not found.")

    paste = PasteService.get_by_id(file["original"])
    if not paste:
        # Paste exists in files table but not in pastes table... remove it.
        config.db.delete("files", {"id": file["id"]})
        abort(404, "File not found.")

    flag = PasteAction.get(flag)
    flag_path = "/" + flag.value if flag.value else ""

    # Get revisions for specified paste
    revisions = config.db.select("revisions", where={"pasteid": paste["id"]})
    # handle any necessary redirects
    if revisions:
        # user navigated to a forked paste, without specifying a commit
        # so redirect to the first commit for the paste.
        redirect_commit = None
        if not commit:
            first_revision = revisions[0]
            if first_revision["fork"]:
                redirect_commit = first_revision["commit"]
        # redirect user to the latest revision if commit is "latest"
        elif commit == "latest":
            latest_revision = revisions[-1]
            redirect_commit = latest_revision["commit"]
        # redirect to the commit if needed
        if redirect_commit:
            redirect(f"/paste/{url}:{redirect_commit}{flag_path}")
    else:
        # redirect to the base paste if there are no commits
        if commit == "latest":
            redirect(f"/paste/{url}{flag_path}")

    # If a commit is provided, get the revision row for that commit
    revision = next(filter(lambda rev: rev["commit"] == commit, revisions), None)

    # List all available commits
    is_fork = False
    commits = ["base"]
    if revisions:
        first_revision = revisions[0]
        is_fork = first_revision["fork"]
        # add the dummy base revision to the revision list
        if not is_fork:
            revisions = ({"commit": "base"},) + revisions
        commits = [row["commit"] for row in revisions]

    # commit provided but is not valid
    if commit and commit not in commits:
        abort(404, "Commit does not exist.")

    # If the given commit does not exist, use the base commit
    if commit not in commits:
        commit = commits[0]

    # Disable the ability to use diff on the base commit only
    # ... but allow forks to be diffed with the original paste
    if (commit == "base" or commit == "") and not is_fork and flag == PasteAction.DIFF:
        redirect(f"/paste/{url}")

    # Add a hit to the paste file
    # Safe to count paste as viewed here since no errors occur after this point
    FileService.increment_hits(file["id"])

    # save the original paste text before we transform it
    raw_paste = revision["paste"] if revision and commit else paste["content"]
    paste["content"] = raw_paste

    # If the user provided the raw flag, skip all HTML rendering
    if flag == PasteAction.RAW:
        response.content_type = "text/plain; charset=utf-8"
        return raw_paste

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

    # highlight the paste if not diffed
    if not content:
        content = functions.highlight_code(paste["content"], lang)

    # Decide whether the viewer owns this file (for forking or editing)
    is_owner = paste["userid"] == SESSION.get("id", 0)

    # Get the styles for syntax highlighting
    css = functions.highlight_code_css()

    # paginate the commits for a post
    pagination = functions.Pagination(
        commits.index(commit or "base") + 1, 1, len(commits), data=revisions
    )

    # Provide the template with a mass of variables
    return template(
        "paste",
        paste=dict(
            id=paste["id"],
            raw=paste["content"],
            content=content,
            lang=lang,
            length=len(raw_paste),
            lines=len(raw_paste.split("\n")),
            own=is_owner,
            url=url,
            hits=file["hits"],
        ),
        title=title,
        css=css,
        revision=revision,
        pagination=pagination,
        flag=flag,
        # Generate a key and password for the edit form
        **key_password_return(SESSION),
    )


@app.route("/<url>")
@app.route("/<url>.<ext>")
@app.route("/<url>/<filename>")
@app.route("/<url>/<filename>.<ext>")
def image_view(url, filename=None, ext=None, file=None, update_hits=True):
    # Use passed results if provided (e.g. by thumbnailer)
    if not file:
        # Check if the requested file exists
        file = FileService.get_by_url(url)
        if not file:
            abort(404, "File not found.")

    # If the file is a paste, redirect to the pastebin
    if file["ext"] == "paste":
        redirect(f"/paste/{url}")

    FileService.abort_if_invalid_url(file, filename, ext)

    # Add a hit to the file
    if update_hits:
        FileService.increment_hits(file["id"])

    return FileService.serve_file(file)


@app.route("/api/thumb/<url>")
@app.route("/api/thumb/<url>.<ext>")
@app.route("/api/thumb/<url>/<filename>")
@app.route("/api/thumb/<url>/<filename>.<ext>")
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
