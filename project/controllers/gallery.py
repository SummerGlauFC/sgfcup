import functools
import hashlib
import os
from functools import partial

from bottle import jinja2_template as template
from bottle import redirect
from bottle import request
from bottle import response

from project import FileType
from project import app
from project import config
from project import configdefines
from project import functions
from project.configdefines import gallery_params
from project.functions import auth_account
from project.functions import delete_files
from project.functions import get_dict
from project.functions import get_paste
from project.functions import get_setting


@app.route("/redirect/gallery/<user_key>")
def gallery_redirect(user_key=None):
    if not user_key:
        redirect("/")
    redirect(f"/gallery/{user_key}")


@app.route("/gallery/", method="GET")
@app.route("/gallery/<user_key>", method="GET")
def gallery_view(user_key=None):
    SESSION = request.environ.get("beaker.session", {})

    key = SESSION.get("key", None)
    # If a user does not provide a gallery to view, redirect to their own
    if not user_key and key:
        redirect(f"/gallery/{key}")
        return ""

    user_id = functions.get_userid(user_key)
    if not user_id:
        return template("error.tpl", error="Specified key does not exist.")

    # Check the users settings to see if they have specified
    # gallery access restrictions
    settings = config.user_settings.get_all_values(user_id)
    get_user_setting = partial(get_dict, settings)

    if get_user_setting("block.value") and get_user_setting("gallery_password.value"):
        auth_cookie = request.get_cookie(f"auth+{user_id}")
        hex_pass = hashlib.sha1(
            get_user_setting("gallery_password.value").encode("utf-8")
        ).hexdigest()
        if not auth_cookie or not hex_pass == auth_cookie:
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
    params.append(user_id)

    total_entries = config.db.fetchone(
        get_search_query("COUNT(`id`) AS `total`"), params
    )["total"]

    # generate pages with a useful pagination class
    pagination = functions.Pagination(page, 30, total_entries)
    results = config.db.fetchall(
        f"{get_search_query('*')} LIMIT {pagination.limit}", params
    )

    if page > pagination.pages:
        if pagination.pages == 0:
            return template("error.tpl", error="There were no results for this search.")
        else:
            return template("error.tpl", error="This page does not exist.")

    for row in results:
        row_file = {}
        # TODO: get latest revision content
        if row["ext"] == "paste":
            paste = get_paste(row["original"])
            row_file["type"] = FileType.PASTE
            row_file["url"] = row["shorturl"]
            row_file["content"] = paste["content"]
            row_file["hits"] = row["hits"]
            row_file["name"] = paste["name"] or row["shorturl"]
            row_file["size"] = len(paste["content"].split("\n"))
            row_file["time"] = {
                "epoch": row["date"].strftime("%s"),
                "timestamp": row["date"].strftime("%d/%m/%Y @ %H:%M:%S"),
            }
        else:
            # is either an image or a file
            path = os.path.join(
                get_setting("directories.files"), row["shorturl"] + row["ext"]
            )
            image = functions.is_image(path)
            if image:
                row_file["type"] = FileType.IMAGE
                row_file["resolution"] = image.size
                image.close()
            else:
                row_file["type"] = FileType.FILE
            row_file["url"] = row["shorturl"]
            row_file["ext"] = row["ext"]
            row_file["original"] = row["original"]
            row_file["hits"] = row["hits"]
            row_file["size"] = functions.sizeof_fmt(row["size"])
            row_file["time"] = {
                "epoch": row["date"].strftime("%s"),
                "timestamp": row["date"].strftime("%d/%m/%Y @ %H:%M:%S"),
            }
        files.append(row_file)

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
        show_ext=get_user_setting("ext.value"),
        hl=functools.partial(functions.hl, search=query, case_sensitive=case),
    )


@app.get("/gallery/auth/<:re:[a-zA-Z0-9_-]+>")
def gallery_auth_view():
    return template("gallery_auth.tpl")


@app.post("/gallery/auth/<user_key:re:[a-zA-Z0-9_-]+>")
def gallery_auth_do(user_key):
    # Set a long cookie to grant a user access to a gallery
    remember = request.forms.get("remember")
    authcode = request.forms.get("authcode")
    name = f"auth+{functions.get_userid(user_key)}"
    value = hashlib.sha1(authcode.encode("utf-8")).hexdigest()
    if remember:
        response.set_cookie(name, value, max_age=3600 * 24 * 7 * 30 * 12, path="/")
    else:
        response.set_cookie(name, value, path="/")
    redirect(f"/gallery/{user_key}")


@app.route("/gallery/delete/advanced", method="GET")
def gallery_delete_advanced_view():
    SESSION = request.environ.get("beaker.session", {})
    return template("delete_advanced.tpl", key=SESSION.get("key", ""))


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

    user = auth_account(key, password)
    if not user:
        return template("delete.tpl", messages=["Key or password is incorrect."])

    sql = f"SELECT * FROM `files` WHERE `userid` = %s AND `{del_type}` {mapping[operator]} %s"
    files = config.db.fetchall(sql, [user["id"], threshold])
    size, count, messages = delete_files(files)
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
    userid = functions.get_userid(key, return_row=True)
    if userid["password"] != password:
        return template("error.tpl", error="Password is incorrect.")
    elif del_type == "Delete Selected" and not files_to_delete:
        return template("error.tpl", error="No files were provided.")

    files = config.db.select("files", where={"userid": userid["id"]})
    source = (
        filter(lambda row: row["shorturl"] in files_to_delete, files)
        if del_type == "Delete Selected"
        else files
    )
    size, count, messages = delete_files(source, messages)

    messages.append(
        f"{count} items deleted. {functions.sizeof_fmt(size)} of disk space saved."
    )

    # Optimize the tables after delete operations
    config.db.execute("OPTIMIZE TABLE `files`")
    config.db.execute("OPTIMIZE TABLE `pastes`")

    return template("delete.tpl", messages=messages, key=key)
