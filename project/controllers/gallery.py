import functools
from typing import Tuple
from urllib.parse import urlencode

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask_login import current_user
from flask_login import login_required
from wtforms import Field

from project import db
from project import functions
from project.constants import FileType
from project.constants import search_modes
from project.constants import sort_modes
from project.forms import flatten_errors
from project.forms.gallery import GalleryAdvancedDeleteForm
from project.forms.gallery import GalleryAuthForm
from project.forms.gallery import GalleryDeleteForm
from project.forms.gallery import GallerySortForm
from project.functions import get_dict
from project.services.account import ACCOUNT_KEY_REGEX
from project.services.account import AccountService
from project.services.file import FileInterface
from project.services.file import FileService
from project.services.gallery import GalleryService
from project.services.paste import PasteInterface
from project.services.paste import PasteService

blueprint = Blueprint("gallery", __name__)


def url_for_page(page):
    """
    Get the URL for a given gallery page.

    :param page: page number to get URL for
    :return: URL for the given gallery page
    """
    form = GallerySortForm(request.args)
    form.page.data = page

    query = {}
    # call iter explicitly to stop typing complaints
    for field in form.__iter__():
        field: Field
        if field.data != field.default:
            query[field.name] = field.data

    encoded = urlencode(query)
    return request.path + (encoded and "?" + urlencode(query))


@blueprint.route("/gallery")
@blueprint.route("/gallery/")
@login_required
def gallery_redirect():
    if current_user.is_authenticated:
        return redirect(f"/gallery/{current_user['key']}")


@blueprint.route("/gallery/<user_key>", methods=["GET"])
def gallery_view(user_key=None):
    form_filter = GallerySortForm(request.args)
    case = form_filter.case.data
    query = form_filter.query.data

    if form_filter.validate():
        page = form_filter.page.data
        query_in = form_filter.in_.data
        active_sort = form_filter.sort.data
        entry_filter = FileType(form_filter.filter.data)
    else:
        # return a generic error if validation failed
        return render_template(
            "error.tpl", error="There were no results for this search."
        )

    user = AccountService.get_by_key(user_key)
    # anonymous account, hide gallery
    if not user or user.get_id() == 0:
        return render_template("error.tpl", error="Specified key does not exist.")

    # Check the users settings to see if they have specified
    # gallery access restrictions
    settings = AccountService.get_settings(user.get_id())
    if not GalleryService.validate_auth_cookie(user.get_id(), settings=settings):
        # if cookie , show password incorrect message
        if GalleryService.get_auth_cookie(user.get_id()):
            flash("Incorrect gallery password", "error")
        return redirect(f"/gallery/auth/{user_key}")

    search_in = search_modes[query_in][1]
    sort_by = sort_modes[active_sort]

    # where clauses
    sql_search = []
    # parameters for the where clauses
    params = []

    if query:
        # Ensure case-sensitive searching with a binary conversion
        collate = " COLLATE utf8_bin" if case else ""
        sql_search.append(f"`{search_in}`{collate} LIKE %s")
        params.append("%" + query + "%")

    # filter results by file type
    if entry_filter != FileType.ALL:
        sql_search.append(f"`type` = %s")
        params.append(entry_filter.value)

    # function that creates a search query given a "what" clause.
    # used to get the total file count, then later
    # use the same query to get the files themselves
    def get_search_query(sub):
        return f"SELECT {sub} FROM `files` WHERE {' AND '.join(sql_search + [''])} `userid` = %s ORDER BY `{sort_by[1]}` {sort_by[2]}"

    params.append(user.get_id())

    total_entries = db.fetchone(get_search_query("COUNT(`id`) AS `total`"), params)[
        "total"
    ]

    # generate pages with a useful pagination class
    pagination = functions.Pagination(page, 30, total_entries)

    if page > pagination.pages:
        if pagination.pages == 0:
            return render_template(
                "error.tpl", error="There were no results for this search."
            )
        else:
            return render_template("error.tpl", error="This page does not exist.")

    # fetch the files given a pagination limit (only fetch files for given page)
    results: Tuple[FileInterface, ...] = db.fetchall(
        f"{get_search_query('*')} LIMIT {pagination.limit}", params
    )

    files = []
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

    usage = None
    tally = db.fetchone(get_search_query("SUM(`size`) AS `total`"), params)
    if tally and tally.get("total"):
        usage = functions.sizeof_fmt(float(tally["total"]))

    form_delete = GalleryDeleteForm()

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
        form_delete=form_delete,
        form_filter=form_filter,
        url_for_page=url_for_page,
    )


@blueprint.route(
    f"/gallery/auth/<regex('{ACCOUNT_KEY_REGEX}'):user_key>", methods=["GET", "POST"]
)
def gallery_auth(user_key):
    # Set a long cookie to grant a user access to a gallery
    form = GalleryAuthForm()
    if form.validate_on_submit():
        user = AccountService.get_by_key(user_key)
        resp = redirect(f"/gallery/{user_key}")
        GalleryService.set_auth_cookie(
            resp, user.get_id(), form.authcode.data, form.remember.data
        )
        return resp
    form.flash_errors()
    return render_template("gallery_auth.tpl", form=form)


@blueprint.route("/gallery/delete/advanced", methods=["GET", "POST"])
@login_required
def gallery_delete_advanced_view():
    form = GalleryAdvancedDeleteForm()
    if form.validate_on_submit():
        mapping = {"lte": "<=", "gte": ">=", "e": "="}
        if current_user.is_authenticated:
            sql = f"SELECT * FROM `files` WHERE `userid` = %s AND `{form.type.data}` {mapping[form.operator.data]} %s"
            files = db.fetchall(sql, [current_user.get_id(), form.threshold.data])
            size, count, messages = FileService.delete_batch(files)
            messages.append(
                f"{count} items deleted. {functions.sizeof_fmt(size)} freed."
            )
            return render_template(
                "delete.tpl", messages=messages, key=current_user["key"]
            )
        flash("Not authenticated", "error")
    form.flash_errors()
    return render_template("delete_advanced.tpl", form=form)


@blueprint.route("/gallery/delete", methods=["POST"])
@login_required
def gallery_delete():
    form = GalleryDeleteForm()
    messages = []

    if form.validate():
        files_to_delete = request.form.getlist("delete_this")

        if form.delete_selected.data and not files_to_delete:
            return render_template("error.tpl", error="No files were provided.")

        files = db.select("files", where={"userid": current_user.get_id()})
        source = (
            filter(lambda row: row["shorturl"] in files_to_delete, files)
            if form.delete_selected.data
            else files
        )
        size, count, messages = FileService.delete_batch(source)

        messages.append(
            f"{count} items deleted. {functions.sizeof_fmt(size)} of disk space saved."
        )

    return render_template(
        "delete.tpl",
        messages=messages or flatten_errors(form.errors),
        key=form.key.data,
    )
