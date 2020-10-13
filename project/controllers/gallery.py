import functools
from typing import Tuple

from bottle import jinja2_template as template
from bottle import redirect
from bottle import request

from project import FileType
from project import app
from project import config
from project import configdefines
from project import functions
from project.configdefines import gallery_params
from project.functions import get_dict
from project.functions import get_session
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
        redirect("/")
    redirect(f"/gallery/{user_key}")


@app.route("/gallery/", method="GET")
@app.route("/gallery/<user_key>", method="GET")
def gallery_view(user_key=None):
    SESSION = get_session()

    key = SESSION.get("key", None)
    # If a user does not provide a gallery to view, redirect to their own
    if not user_key and key:
        redirect(f"/gallery/{key}")
        return ""

    user = AccountService.get_by_key(user_key)
    # anonymous account, hide gallery
    if not user or user["id"] == 0:
        return template("error.tpl", error="Specified key does not exist.")

    # Check the users settings to see if they have specified
    # gallery access restrictions
    settings = AccountService.get_settings(user["id"])
    if not AccountService.validate_auth_cookie(user["id"], settings=settings):
        redirect(f"/gallery/auth/{user_key}")

    files = []

    # shorthand assignments for often used data
    page = int(request.query.get("page", gallery_params["page"]))
    case = int(request.query.get("case", gallery_params["case"]))
    query_in = functions.get_inrange(
        request.query.get("in"),
        int(gallery_params["in"]),
        len(configdefines.search_modes),
    )
    query = request.query.get("query", "")
    active_sort = functions.get_inrange(
        request.query.get("sort"),
        int(gallery_params["sort"]),
        len(configdefines.sort_modes),
    )

    sql_search = ""
    search_in = configdefines.search_modes[query_in][1]
    sort_by = configdefines.sort_modes[active_sort]

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

    total_entries = config.db.fetchone(
        get_search_query("COUNT(`id`) AS `total`"), params
    )["total"]

    # generate pages with a useful pagination class
    pagination = functions.Pagination(page, 30, total_entries)
    results: Tuple[FileInterface, ...] = config.db.fetchall(
        f"{get_search_query('*')} LIMIT {pagination.limit}", params
    )

    if page > pagination.pages:
        if pagination.pages == 0:
            return template("error.tpl", error="There were no results for this search.")
        else:
            return template("error.tpl", error="This page does not exist.")

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
        }
        if row["ext"] == "paste":
            paste: PasteInterface = PasteService.get_by_id(row["original"])
            file["type"] = FileType.PASTE
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
            file["type"] = FileType.FILE
            file["size"] = functions.sizeof_fmt(row["size"])
            path = FileService.get_file_path(row)
            image = functions.is_image(path)
            if image:
                file["type"] = FileType.IMAGE
                file["resolution"] = image.size
                image.close()
        files.append(file)

    tally = config.db.fetchone(get_search_query("SUM(`size`) AS `total`"), params)
    usage = None
    if tally and tally["total"] is not None:
        usage = functions.sizeof_fmt(float(tally["total"]))

    return template(
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


@app.get(f"/gallery/auth/<:re:{ACCOUNT_KEY_REGEX}>")
def gallery_auth_view():
    return template("gallery_auth.tpl")


@app.post(f"/gallery/auth/<user_key:re:{ACCOUNT_KEY_REGEX}>")
def gallery_auth_do(user_key):
    # Set a long cookie to grant a user access to a gallery
    remember = request.forms.get("remember")
    authcode = request.forms.get("authcode")
    user = AccountService.get_by_key(user_key)
    AccountService.set_auth_cookie(user["id"], authcode, remember)
    redirect(f"/gallery/{user_key}")


@app.route("/gallery/delete/advanced", method="GET")
def gallery_delete_advanced_view():
    SESSION = get_session()
    return template("delete_advanced.tpl", **key_password_return(SESSION))


@app.route("/gallery/delete/advanced", method="POST")
def gallery_delete_advanced():
    # get relevant parameters for the query
    mapping = {"lte": "<=", "gte": ">=", "e": "="}
    operator = request.forms.get("operator")
    del_type = request.forms.get("type")
    key = request.forms.get("key")
    password = request.forms.get("password")
    threshold = request.forms.get("threshold", None)
    if not (
        operator in mapping.keys()
        and del_type in ["hits", "size"]
        and key
        and password
        and threshold is not None
    ):
        return template("delete.tpl", messages=["Invalid request. Please try again."])

    user, is_authed = AccountService.authenticate(key, password)
    if not user:
        return template("delete.tpl", messages=["Key or password is incorrect."])

    sql = f"SELECT * FROM `files` WHERE `userid` = %s AND `{del_type}` {mapping[operator]} %s"
    files = config.db.fetchall(sql, [user["id"], threshold])
    size, count, messages = FileService.delete_batch(files)
    messages.append(f"{count} items deleted. {functions.sizeof_fmt(size)} freed.")
    return template("delete.tpl", messages=messages, key=key)


@app.route("/gallery/delete", method="POST")
def gallery_delete():
    files_to_delete = request.forms.getall("delete_this")
    key = request.forms.get("key")
    password = request.forms.get("password")
    del_type = request.forms.get("type")

    messages = []

    # Only allow valid deletion types
    if del_type not in ["Delete Selected", "Delete All"]:
        return template("error.tpl", error="Invalid deletion type provided.")

    # Check if user details are correct
    user = AccountService.get_by_key(key)
    if user["password"] != password:
        return template("error.tpl", error="Password is incorrect.")
    if del_type == "Delete Selected" and not files_to_delete:
        return template("error.tpl", error="No files were provided.")

    files = config.db.select("files", where={"userid": user["id"]})
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
    config.db.execute("OPTIMIZE TABLE `files`")
    config.db.execute("OPTIMIZE TABLE `pastes`")

    return template("delete.tpl", messages=messages, key=key)
