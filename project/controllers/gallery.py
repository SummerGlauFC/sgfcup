import functools
from typing import Tuple

from flask import redirect
from flask import render_template
from flask import request
from flask import session

from project import app
from project import db
from project import functions
from project.constants import FileType
from project.constants import gallery_params
from project.constants import search_modes
from project.constants import sort_modes
from project.functions import get_dict
from project.functions import key_password_return
from project.services.account import ACCOUNT_KEY_REGEX
from project.services.account import AccountService
from project.services.file import FileInterface
from project.services.file import FileService
from project.services.paste import PasteInterface
from project.services.paste import PasteService


@app.route("/redirect/gallery/<user_key>")
def gallery_redirect(user_key=None):
    if not user_key:
        return redirect("/")
    return redirect(f"/gallery/{user_key}")


@app.route("/gallery/", methods=["GET"])
@app.route("/gallery/<user_key>", methods=["GET"])
def gallery_view(user_key=None):
    key = session.get("key", None)
    # If a user does not provide a gallery to view, redirect to their own
    if not user_key and key:
        return redirect(f"/gallery/{key}")

    user = AccountService.get_by_key(user_key)
    # anonymous account, hide gallery
    if not user or user["id"] == 0:
        return render_template("error.tpl", error="Specified key does not exist.")

    # Check the users settings to see if they have specified
    # gallery access restrictions
    settings = AccountService.get_settings(user["id"])
    if not AccountService.validate_auth_cookie(user["id"], settings=settings):
        return redirect(f"/gallery/auth/{user_key}")

    files = []

    # shorthand assignments for often used data
    page = int(request.args.get("page", gallery_params["page"]))
    case = int(request.args.get("case", gallery_params["case"]))
    query_in = functions.get_inrange(
        request.args.get("in"),
        int(gallery_params["in"]),
        len(search_modes),
    )
    query = request.args.get("query", "")
    active_sort = functions.get_inrange(
        request.args.get("sort"),
        int(gallery_params["sort"]),
        len(sort_modes),
    )

    sql_search = ""
    search_in = search_modes[query_in][1]
    sort_by = sort_modes[active_sort]

    # Ensure case-sensitive searching with a binary conversion
    collate = " COLLATE utf8_bin" if case else ""

    if query:
        sql_search = f"`{search_in}`{collate} LIKE %s AND"

    def get_search_query(sub):
        return f"SELECT {sub} FROM `files` WHERE {sql_search} `userid` = %s ORDER BY `{sort_by[1]}` {sort_by[2]}"

    params = []
    if query:
        params = ["%" + query + "%"]
    params.append(user["id"])

    total_entries = db.fetchone(get_search_query("COUNT(`id`) AS `total`"), params)[
        "total"
    ]

    # generate pages with a useful pagination class
    pagination = functions.Pagination(page, 30, total_entries)
    results: Tuple[FileInterface, ...] = db.fetchall(
        f"{get_search_query('*')} LIMIT {pagination.limit}", params
    )

    if page > pagination.pages:
        if pagination.pages == 0:
            return render_template(
                "error.tpl", error="There were no results for this search."
            )
        else:
            return render_template("error.tpl", error="This page does not exist.")

    for row in results:
        file = {
            "url": row["shorturl"],
            "hits": row["hits"],
            "time": {
                "epoch": row["date"].timestamp(),
                "timestamp": row["date"].strftime("%d/%m/%Y @ %H:%M:%S"),
            },
            "ext": row["ext"],
            "original": row["original"],
            "type": FileType(row["type"]),
        }
        if file["type"] == FileType.PASTE:
            paste: PasteInterface = PasteService.get_by_id(row["original"])
            file["content"] = paste["content"]
            file["name"] = paste["name"] or row["shorturl"]
            file["size"] = len(file["content"].split("\n"))

            # get latest revision for paste
            latest_rev = PasteService.get_latest_revision(paste)
            if latest_rev:
                file["content"] = latest_rev["paste"]
                # add latest commit hash to url
                file["url"] = row["shorturl"] + ":" + latest_rev["commit"]
        else:
            file["size"] = functions.sizeof_fmt(row["size"])
            if file["type"] == FileType.IMAGE:
                file["resolution"] = (row["width"], row["height"])
        files.append(file)

    tally = db.fetchone(get_search_query("SUM(`size`) AS `total`"), params)
    usage = None
    if tally and tally["total"] is not None:
        usage = functions.sizeof_fmt(float(tally["total"]))

    return render_template(
        "gallery.tpl",
        key=user_key,
        pages=pagination,
        usage=usage,
        entries=total_entries,
        active_sort=active_sort,
        search={"query": query, "in": query_in, "case": case},
        files=files,
        xhr=request.headers.get("X-AJAX", "false") == "true",
        show_ext=get_dict(settings, "ext.value"),
        hl=functools.partial(
            functions.highlight_text, search=query, case_sensitive=case
        ),
    )


@app.route(f"/gallery/auth/<regex('{ACCOUNT_KEY_REGEX}'):_>", methods=["GET"])
def gallery_auth_view(_):
    return render_template("gallery_auth.tpl")


@app.route(f"/gallery/auth/<regex('{ACCOUNT_KEY_REGEX}'):user_key>", methods=["POST"])
def gallery_auth_do(user_key):
    # Set a long cookie to grant a user access to a gallery
    remember = request.form.get("remember")
    authcode = request.form.get("authcode")
    user = AccountService.get_by_key(user_key)
    resp = redirect(f"/gallery/{user_key}")
    AccountService.set_auth_cookie(resp, user["id"], authcode, remember)
    return resp


@app.route("/gallery/delete/advanced", methods=["GET"])
def gallery_delete_advanced_view():
    return render_template("delete_advanced.tpl", **key_password_return())


@app.route("/gallery/delete/advanced", methods=["POST"])
def gallery_delete_advanced():
    # get relevant parameters for the query
    mapping = {"lte": "<=", "gte": ">=", "e": "="}
    operator = request.form.get("operator")
    del_type = request.form.get("type")
    key = request.form.get("key")
    password = request.form.get("password")
    threshold = request.form.get("threshold", None)
    if not (
        operator in mapping.keys()
        and del_type in ["hits", "size"]
        and key
        and password
        and threshold is not None
    ):
        return render_template(
            "delete.tpl", messages=["Invalid request. Please try again."]
        )

    user, is_authed = AccountService.authenticate(key, password)
    if not user:
        return render_template("delete.tpl", messages=["Key or password is incorrect."])

    sql = f"SELECT * FROM `files` WHERE `userid` = %s AND `{del_type}` {mapping[operator]} %s"
    files = db.fetchall(sql, [user["id"], threshold])
    size, count, messages = FileService.delete_batch(files)
    messages.append(f"{count} items deleted. {functions.sizeof_fmt(size)} freed.")
    return render_template("delete.tpl", messages=messages, key=key)


@app.route("/gallery/delete", methods=["POST"])
def gallery_delete():
    files_to_delete = request.form.getlist("delete_this")
    key = request.form.get("key")
    password = request.form.get("password")
    del_type = request.form.get("type")

    messages = []

    # Only allow valid deletion types
    if del_type not in ["Delete Selected", "Delete All"]:
        return render_template("error.tpl", error="Invalid deletion type provided.")

    # Check if user details are correct
    user = AccountService.get_by_key(key)
    if user["password"] != password:
        return render_template("error.tpl", error="Password is incorrect.")
    if del_type == "Delete Selected" and not files_to_delete:
        return render_template("error.tpl", error="No files were provided.")

    files = db.select("files", where={"userid": user["id"]})
    source = (
        filter(lambda row: row["shorturl"] in files_to_delete, files)
        if del_type == "Delete Selected"
        else files
    )
    size, count, messages = FileService.delete_batch(source, messages)

    messages.append(
        f"{count} items deleted. {functions.sizeof_fmt(size)} of disk space saved."
    )

    # Optimize the tables after delete operations
    db.execute("OPTIMIZE TABLE `files`")
    db.execute("OPTIMIZE TABLE `pastes`")

    return render_template("delete.tpl", messages=messages, key=key)
