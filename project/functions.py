import functools
import os
import random
import re
import string
from builtins import range
from functools import partial
from math import ceil
from typing import Optional

import magic
import markupsafe
import pygments
from PIL import Image
from flask import Response
from flask import jsonify
from flask import make_response
from flask import request
from flask import send_from_directory
from flask import session
from pygments.formatters import HtmlFormatter
from pygments.lexers import PhpLexer
from pygments.lexers import TextLexer
from pygments.lexers import get_all_lexers
from pygments.lexers import get_lexer_by_name
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound
from werkzeug.routing import BaseConverter
from werkzeug.urls import url_quote

from db import DB
from project import config


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def id_generator(size=6, chars=string.ascii_letters + string.digits):
    """ Generates a random string of given size """
    return "".join(random.SystemRandom().choice(chars) for _ in range(size))


def is_image(path):
    """ Check if a path is an image with PIL, and return the image object """
    try:
        im = Image.open(path)
    except IOError:
        return None
    return im


def highlight_text(text, search, case_sensitive=False):
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


def list_languages():
    """List all languages."""
    languages = list(get_all_lexers())
    languages.sort(key=lambda x: x[0].lstrip(" _-.").lower())
    return languages


def highlight_code(code, language, _preview=False, _linenos=True):
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


def highlight_code_css(style="xcode", css_class=".syntax"):
    """ Gets the CSS for pygments """
    return HtmlFormatter(style=style).get_style_defs(css_class)


def json_response(success=True, error=False, status=200, **body):
    """
    Return a JSON response.

    :param success: if the request was successful
    :param error: error if applicable else False
    :param status: status code (default 200)
    :param body: any extra parameters to expand into the response
    :return: a JSON response
    """
    resp: Response = jsonify(
        {"success": success, "error": error, "status_code": status, **body}
    )
    resp.status_code = status
    return resp


class Error(Exception):
    status_code = 400

    def __init__(self, error, status=None, errors=None):
        super().__init__(self)
        if status is not None:
            self.status_code = status
        self.error = error
        self.errors = errors

    def response(self):
        resp = dict(success=False, error=self.error, status=self.status_code)
        if self.errors:
            resp.update(errors=self.errors)
        return json_response(**resp)


def json_error(error, status=400, errors=None):
    """
    Return an Error exception.

    :param error: main error string
    :param status: status code (default 400)
    :param errors: form errors if applicable
    :return: Error exception
    """
    return Error(error, status, errors)


# from https://stackoverflow.com/a/36131992
def get_dict(dictionary, dotted_key):
    keys = dotted_key.split(".")
    return functools.reduce(lambda d, key: d.get(key) if d else None, keys, dictionary)


get_setting = partial(get_dict, config.Settings)


def remove_transparency(im, bg_colour=(255, 255, 255)):
    # courtesy of Humphrey@stackoverflow
    # https://stackoverflow.com/a/35859141

    # Only process if image has transparency
    # (http://stackoverflow.com/a/1963146)
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        # Need to convert to RGBA if LA format due to a bug in PIL
        alpha = im.convert("RGBA").split()[-1]
        background = Image.new("RGB", im.size, bg_colour)
        background.paste(im, mask=alpha)
        return background
    else:
        return im


def get_host() -> str:
    """ Get the schema + host """
    return "{}://{}".format(
        "https" if get_setting("ssl") else "http",
        request.environ.get("HTTP_HOST"),
    )


def static_file(path: str, root: str, filename: Optional[str] = None) -> Response:
    file_path = os.path.join(root, path)
    mime = magic.from_file(file_path, mime=True)

    def set_file_info(resp):
        resp.headers.set("Content-Type", mime)
        if filename:
            resp.headers.set(
                "Content-Disposition",
                "inline",
                **{"filename*": "UTF-8''%s" % url_quote(filename)},
            )
        return resp

    # Use the sendfile built into nginx if it's available
    if get_setting("use_nginx_sendfile"):
        folder = "t" if root is get_setting("directories.thumbs") else "p"
        response = set_file_info(make_response())
        response.headers.set("X-Accel-Redirect", f"/get_image/{folder}/{path}")
        return response

    response = make_response(send_from_directory(root, path, mimetype=mime))
    return set_file_info(response)


def key_password_return():
    """
    Check if the user has got their key and password stored, else
    generate a mostly secure key for them.

    :return: dict containing {key: ..., password: ...}
    """
    if session.get("id"):
        return {"key": session.get("key"), "password": session.get("password")}
    return {"key": id_generator(15), "password": id_generator(15)}


def connect_db():
    """
    Get a DB connection instance.

    :return: DB connection instance
    """
    return DB(
        user=get_setting("database.user"),
        password=get_setting("database.password"),
        database=get_setting("database.db"),
        debug=get_setting("debug.enabled"),
    )
