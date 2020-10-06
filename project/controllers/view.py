import os

import ghdiff
import magic
from PIL import Image
from PIL import ImageOps
from bottle import abort
from bottle import jinja2_template as template
from bottle import redirect
from bottle import request
from bottle import response
from bottle import static_file as bottle_static_file

from project import app
from project import config
from project import functions
from project.configdefines import PasteAction
from project.functions import abort_if_invalid_image_url
from project.functions import get_parent_paste
from project.functions import get_setting
from project.functions import remove_transparency


def static_file(path, root, filename=False):
    file_path = root + path
    mime = magic.from_file(file_path, mime=True)

    def set_file_info(resp):
        resp.set_header("Content-Type", mime)
        if filename:
            resp.set_header("Content-Disposition", f'inline; filename="{filename}"')
        return resp

    set_file_info(response)

    # Use the sendfile built into nginx if it's available
    if config.Settings["use_nginx_sendfile"]:
        # TODO: use paths from settings
        folder = "t" if root is get_setting("directories.thumbs") else "p"

        response.set_header("X-Accel-Redirect", f"/get_image/{folder}/{path}")

        return "This should be handled by nginx."

    return set_file_info(bottle_static_file(path, root=root, mimetype=mime))


@app.route("/api/thumb/<url>")
@app.route("/api/thumb/<url>.<ext>")
@app.route("/api/thumb/<url>/<filename>")
@app.route("/api/thumb/<url>/<filename>.<ext>")
def api_thumb(url, filename=None, ext=None, temp=False, size=(400, 400)):
    # Thumbnailer route
    # Generated for the gallery

    # Return the currently saved thumbnail if it exists
    thumb_file = f"thumb_{url}.jpg"
    thumb_dir = get_setting("directories.thumbs")
    if os.path.exists(os.path.join(thumb_dir, thumb_file)) and not temp:
        return static_file(thumb_file, root=thumb_dir)
    elif os.path.exists(os.path.join("/tmp", thumb_file)) and temp:
        return static_file(thumb_file, root="/tmp/")
    else:
        # Select the full file from the database
        results = config.db.fetchone(
            "SELECT * FROM `files` WHERE BINARY `shorturl` = %s", [url]
        )

        if results:
            abort_if_invalid_image_url(results, filename, ext)
            # Generate a 400x400 (by default) JPEG thumbnail
            base = Image.open(
                os.path.join(
                    get_setting("directories.files"),
                    results["shorturl"] + results["ext"],
                )
            )
            if size < base.size:
                image_info = base.info
                # if base.mode not in ('L', 'RGBA'):
                #     base = base.convert('RGBA')
                base = ImageOps.fit(base, size, Image.ANTIALIAS)
                save_dir = "/tmp/" if temp else thumb_dir
                base = remove_transparency(base)
                base.save(os.path.join(save_dir, thumb_file), **image_info)
                return static_file(thumb_file, root=save_dir)
            return image_view(url, filename, ext, results=results, update_hits=False)
        else:
            abort(404, "File not found.")


@app.route("/paste/<url>")
@app.route("/paste/<url>/<flag>")
def paste_view(url, flag=None):
    SESSION = request.environ.get("beaker.session", {})

    # Extract the commit from the URL, if it exists.
    if ":" in url:
        url, commit = url.split(":", 1)
    else:
        commit = False

    # Select the paste from `files`
    file = config.db.fetchone(
        "SELECT * FROM `files` WHERE BINARY `shorturl` = %s", [url]
    )
    if not file:
        abort(404, "File not found.")

    paste = config.db.select("pastes", where={"id": file["original"]}, singular=True)
    if not paste:
        # Paste exists in files table but not in pastes table... remove it.
        config.db.delete("files", {"id": file["id"]})
        abort(404, "File not found.")

    flag = PasteAction.get(flag)
    flag_path = "/" + flag.value if flag.value else ""

    # Get revisions for specified paste
    revisions = config.db.select("revisions", where={"pasteid": paste["id"]})
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
        if redirect_commit:
            redirect(f"/paste/{url}:{redirect_commit}{flag_path}")
    else:
        # redirect to the base paste if there are no commits
        if commit == "latest":
            redirect(f"/paste/{url}{flag_path}")

    # Add a hit to the paste
    config.db.execute("UPDATE `files` SET `hits`=`hits`+1 WHERE `id`=%s", [file["id"]])

    # Decide whether the viewer owns this file (for forking or editing)
    is_owner = paste["userid"] == SESSION.get("id", 0)

    # If a commit is provided, get the row for that revision
    revision = next(filter(lambda rev: rev["commit"] == commit, revisions), None)

    is_fork = False

    commits = []
    # Append every commit which exists
    if revisions:
        first_revision = revisions[0]
        is_fork = first_revision["fork"]
        # add the dummy base revision to the revision list
        if not is_fork:
            revisions = ({"commit": "base"},) + revisions
        for row in revisions:
            commits.append(row["commit"])
    else:
        commits = ["base"]

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

    # If the user provided the raw flag, skip all HTML rendering
    if flag == PasteAction.RAW:
        response.content_type = "text/plain; charset=utf-8"
        return revision["paste"] if revision and commit else paste["content"]

    # Check if the paste has a name, and show the name if it does.
    name = paste["name"]
    title = f"Paste: {name or url}"
    lang = paste["lang"]

    # save the original paste text before we transform it
    # for statistics
    raw_paste = paste["content"]

    # Check if to make a diff or not,
    # depending on if the revision exists
    if revision:
        raw_paste = revision["paste"]
        paste["content"] = raw_paste

        parent, parent_commit, parent_content = get_parent_paste(revision)
        if flag == PasteAction.DIFF:
            # diff with parent paste
            paste["content"] = ghdiff.diff(parent_content, revision["paste"], css=False)

        # Add the parent pastes URL to the revision's data.
        revision["parent_url"] = parent["shorturl"] + (
            ":" + parent_commit if parent_commit else ""
        )

        title += f' [{revision["commit"]}]'

    # Get meta data about the pastes
    length = len(raw_paste)
    lines = len(raw_paste.split("\n"))
    hits = file["hits"]

    # Decide whether to diff the
    diffing = flag == PasteAction.DIFF and commit in commits
    if diffing:
        content = paste["content"]
    else:
        content = functions.highlight(paste["content"], lang)

    # Get the styles for syntax highlighting
    css = functions.css()

    # Generate a key and password for the edit form
    if SESSION.get("id"):
        key = SESSION.get("key")
        password = SESSION.get("password")
    else:
        key = functions.id_generator(15)
        password = functions.id_generator(15)

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
            length=length,
            lines=lines,
            own=is_owner,
            url=url,
            hits=hits,
        ),
        title=title,
        css=css,
        key=key,
        password=password,
        revision=revision,
        pagination=pagination,
        flag=flag,
    )


@app.route("/<url>")
@app.route("/<url>.<ext>")
@app.route("/<url>/<filename>")
@app.route("/<url>/<filename>.<ext>")
def image_view(url, filename=None, ext=None, results=None, update_hits=True):
    # Check if the requested file exists
    # Also, use a passed-through results if it exists.
    if not results:
        results = config.db.fetchone(
            "SELECT * FROM `files` WHERE BINARY `shorturl` = %s", [url]
        )

    if results:
        abort_if_invalid_image_url(results, filename, ext)

        # If the file is a paste, redirect to the pastebin
        if results["ext"] == "paste":
            redirect(f"/paste/{url}")
        else:
            # Add one hit to the file
            if update_hits:
                config.db.execute(
                    "UPDATE `files` SET `hits`=`hits`+1 WHERE `id`=%s", [results["id"]]
                )

            return static_file(
                results["shorturl"] + results["ext"],
                root=get_setting("directories.files"),
                filename=results["original"],
            )

    abort(404, "File not found.")
