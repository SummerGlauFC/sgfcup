import functools
import inspect
import os
import random
import re
import string
from builtins import range
from functools import partial
from math import ceil
from urllib.parse import urlencode

import magic
import markupsafe
import pygments
from PIL import Image
from bottle import HTTPResponse
from bottle import abort
from bottle import request
from bottle import response
from bottle import static_file as bottle_static_file
from pygments.formatters import HtmlFormatter
from pygments.lexers import PhpLexer
from pygments.lexers import TextLexer
from pygments.lexers import get_all_lexers
from pygments.lexers import get_lexer_by_name
from pygments.lexers import get_lexer_for_filename
from pygments.lexers import get_lexer_for_mimetype
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound

from project import config
from project import config
from project.configdefines import gallery_params


def id_generator(size=6, chars=string.ascii_letters + string.digits):
    """ Generates a random string of given size """
    return "".join(random.SystemRandom().choice(chars) for _ in range(size))


def strs_to_ints(dicts):
    """ Converts all strings which are ints in a dict to actual ints
        (for bottle GET/POST variables) """
    new = {}

    for key, value in dicts.iteritems():
        new[key] = int(value) if value.isdigit() else value

    return new


def is_image(path):
    """ Check if a path is an image with PIL, and return the image object """
    try:
        im = Image.open(path)
    except IOError:
        return False
    return im


def hl(text, search, case_sensitive=False):
    """ Use regex to highlight all occurrences of a substring in a string """
    if not search:
        return text

    output = ""
    i = 0
    text = markupsafe.escape(text)
    regex = re.compile(
        r"(" + re.escape(search) + ")", re.I if not case_sensitive else 0
    )
    for m in regex.finditer(text):
        output += "".join(
            [
                text[i : m.start()],
                '<span class="hl">',
                text[m.start() : m.end()],
                "</span>",
            ]
        )
        i = m.end()
    return "".join([output, text[i:]])


def get_userid(key, return_row=False):
    """ Gets a users ID from their `key` """
    userid = config.db.select("accounts", where={"key": key}, singular=True)
    if userid:
        return userid["id"] if not return_row else userid
    return None


def get_inrange(get, default, highest):
    """ Checks if an int is in a range """
    if get and get.isdigit() and int(get) in range(highest):
        return int(get)
    return default


def sizeof_fmt(num, short=None):
    """ Bytes to a human-readable format """
    for x in ["bytes", "KB", "MB", "GB"]:
        if 1024.0 > num > -1024.0:
            return "%3.2f %s" % (num, x) if not short else "%3.0f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, "TB")


class Pagination(object):
    def __init__(self, page, per_page, total_count, data=None):
        """
        Allows easy pagination implementation

        :param page: current page
        :param per_page: items per page
        :param total_count: total number of items
        :param data: list of data to use for pages instead of numbers
        """
        self.page = page
        self.per_page = per_page
        self.total_count = total_count
        self.data = data or range(1, self.pages + 1)

    @property
    def current_page(self):
        return self.data[self.page - 1]

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def next_page(self):
        return self.page + 1 if self.page + 1 <= self.pages else self.page

    @property
    def prev_page(self):
        return self.page - 1 if self.page > 1 else self.page

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def limit(self):
        return f"{self.per_page * (self.page - 1)},{self.per_page}"

    def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if (
                num <= left_edge
                or (self.page - left_current - 1 < num < self.page + right_current)
                or num > self.pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield self.data[num - 1]
                last = num


def get_language_for(filename, mimetype=None, default="text"):
    """Get language for filename and mimetype"""
    try:
        if mimetype is None:
            raise ClassNotFound()
        lexer = get_lexer_for_mimetype(mimetype)
    except ClassNotFound:
        try:
            lexer = get_lexer_for_filename(filename)
        except ClassNotFound:
            return default
    return get_known_alias(lexer, default)


def get_language_for_code(code, mimetype=None, default="text"):
    """Get language for filename and mimetype"""
    try:
        lexer = guess_lexer(code)
    except ClassNotFound:
        return default
    return get_known_alias(lexer, default)


def lookup_language_alias(alias, default="text"):
    """When passed a pygments alias returns the alias from LANGUAGES. If
the alias does not exist at all or is not in languages, `default` is
returned.
"""
    if alias in get_all_lexers():
        return alias
    try:
        lexer = get_lexer_by_name(alias)
    except ClassNotFound:
        return default
    return get_known_alias(lexer)


def get_known_alias(lexer, default="text"):
    """Return the known alias for the lexer."""
    for alias in lexer.aliases:
        if alias in get_all_lexers():
            return alias
    return default


def list_languages():
    """List all languages."""
    languages = list(get_all_lexers())
    languages.sort(key=lambda x: x[0].lstrip(" _-.").lower())
    return languages


def highlight(code, language, _preview=False, _linenos=True):
    """ Syntax highlights a code file """
    if language == "php":
        lexer = PhpLexer(startinline=True)
    elif language == "guess":
        lexer = guess_lexer(code)
    else:
        try:
            lexer = get_lexer_by_name(language)
        except ClassNotFound:
            lexer = TextLexer()
    formatter = HtmlFormatter(linenos=_linenos, cssclass="syntax", style="xcode")
    return f'<div class="syntax">{pygments.highlight(code, lexer, formatter)}</div>'


def css(style="xcode", css_class=".syntax"):
    """ Gets the CSS for pygments """
    return HtmlFormatter(style=style).get_style_defs(css_class)


def json_response(success=True, error=False, status=200, **body):
    return HTTPResponse(
        body={"success": success, "error": error, "status_code": status, **body},
        status=status,
    )


def json_error(error, status=400):
    return json_response(success=False, error=error, status=status)


# from https://stackoverflow.com/a/36131992
def get_dict(dictionary, dotted_key):
    keys = dotted_key.split(".")
    return functools.reduce(lambda d, key: d.get(key) if d else None, keys, dictionary)


get_setting = partial(get_dict, config.Settings)


def debug_print(*args, trace=True):
    print(args)
    if trace:
        (
            frame,
            filename,
            line_number,
            function_name,
            lines,
            index,
        ) = inspect.getouterframes(inspect.currentframe())[2]

        lines = "\n".join([x.strip() for x in lines])
        print(f"\t{filename}:{line_number} in {function_name}\n\t-->\t{lines}")
    print("-" * 40)


def get_or_create_account(key, password):
    if not key:
        # if no key is provided, anonymous upload
        return True, 0

    # Keys must only contain alphanumerics and underscores/hyphens
    if not re.match("^[a-zA-Z0-9_-]+$", key):
        raise json_error(
            "Invalid key given. (can only contain letters, numbers, underscores and hyphens)"
        )

    # Check if the specified account already exists.
    user = config.db.select("accounts", where={"key": key}, singular=True)

    # If it does, check their password is correct.
    if user:
        is_authed = user["password"] == password
        user_id = user["id"]
    else:
        # If the account doesn't exist, make a new account.
        new_account = config.db.insert("accounts", {"key": key, "password": password})
        user_id = new_account.lastrowid
        is_authed = True

    return is_authed, user_id


def remove_transparency(im, bg_colour=(255, 255, 255)):
    # courtesy of Humphrey@stackoverflow
    # https://stackoverflow.com/a/35859141

    # Only process if image has transparency
    # (http://stackoverflow.com/a/1963146)
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        # Need to convert to RGBA if LA format due to a bug in PIL
        # (http://stackoverflow.com/a/1963146)
        alpha = im.convert("RGBA").split()[-1]
        background = Image.new("RGB", im.size, bg_colour)
        background.paste(im, mask=alpha)  # 3 is the alpha channel
        return background
    else:
        return im


def abort_if_invalid_image_url(file, filename, ext):
    use_extensions = config.user_settings.get(file["userid"], "ext")
    should_abort = False
    if filename:
        # Check for extensionless files first (e.g. Dockerfile)
        if not ext and filename != file["original"]:
            should_abort = True
        if ext and "{}.{}".format(filename, ext) != file["original"]:
            should_abort = True
    else:
        # don't resolve if longer filename setting set, and the filename is not included.
        if use_extensions == 2:
            should_abort = True
        if ext and ".{}".format(ext) != file["ext"]:
            should_abort = True
    if should_abort:
        abort(404, "File not found.")


def get_host() -> str:
    """ Get the schema + host """
    return "{}://{}".format(
        "https" if get_setting("ssl") else "http", request.environ.get("HTTP_HOST"),
    )


def get_file(shorturl: str):
    return config.db.fetchone(
        "SELECT * FROM `files` WHERE BINARY `shorturl` = %s", [shorturl]
    )


def add_file_hit(file_id: int):
    config.db.execute("UPDATE `files` SET `hits`=`hits`+1 WHERE `id`=%s", [file_id])


def get_paste(paste_id: int):
    return config.db.select("pastes", where={"id": paste_id}, singular=True)


def get_paste_revision(**kwargs):
    return config.db.select("revisions", where=kwargs, singular=True)


def get_paste_content(shorturl: str = None, commit: str = None, paste=None):
    if not paste:
        file = get_file(shorturl)
        if not file:
            return None
        paste = paste or get_paste(file["original"])
        if not paste:
            return None
    revision = get_paste_revision(pasteid=paste["id"], commit=commit)
    if revision:
        return revision["paste"]
    elif paste:
        return paste["content"]
    return None


def get_parent_paste(rev):
    parent_commit = None
    if rev["parent_revision"]:
        parent_rev = get_paste_revision(id=rev["parent_revision"])
        parent_commit = parent_rev["commit"]
        parent = get_paste(parent_rev["pasteid"])
    else:
        parent = get_paste(rev["parent"])
    parent_content = get_paste_content(commit=parent_commit, paste=parent)
    return parent, parent_commit, parent_content


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
    if get_setting("use_nginx_sendfile"):
        # TODO: use paths from settings
        folder = "t" if root is get_setting("directories.thumbs") else "p"
        response.set_header("X-Accel-Redirect", f"/get_image/{folder}/{path}")
        return "This should be handled by nginx."

    return set_file_info(bottle_static_file(path, root=root, mimetype=mime))


def url_for_page(page):
    """
    Get the URL for a given gallery page.

    :param page: page number to get URL for
    :return: URL for the given gallery page
    """

    request.query["page"] = str(page)
    query = {}
    for key, value in request.query.items():
        if value != gallery_params.get(key):
            query[key] = value

    encoded = urlencode(query)
    return request.urlparts.path + (encoded and "?" + urlencode(query))


def delete_file(file):
    size = file["size"]
    shorturl = file["shorturl"]
    original = file["original"]

    config.db.delete("files", {"shorturl": shorturl})

    # Special treatment for pastes as they don't physically exist
    # on the disk
    if file["ext"] == "paste":
        config.db.delete("pastes", {"id": original})
        # TODO: delete revisions of the deleted paste
        output = f"Removed paste {shorturl}"
    else:
        try:
            os.remove(get_setting("directories.files") + shorturl + file["ext"])
            output = f'Removed file "{original}" ({shorturl})'
        except OSError:
            output = f"Could not delete {shorturl}"

    return size, output


def delete_files(to_delete, output=None):
    size = 0
    count = 0

    if output is None:
        output = []

    for row in to_delete:
        file_size, file_output = delete_file(row)
        count += 1
        size += file_size
        output.append(file_output)

    return size, count, output


def auth_account(key, password):
    return config.db.select(
        "accounts", where={"key": key, "password": password}, singular=True,
    )


def key_password_return(session):
    # Check if the user has got their key and password stored, else
    # generate a mostly secure key for them.
    if session.get("id"):
        return {"key": session.get("key"), "password": session.get("password")}
    return {"key": functions.id_generator(15), "password": functions.id_generator(15)}
