import functools
import os
import random
import re
import string
from builtins import range
from functools import partial
from math import ceil
from typing import Optional
from urllib.parse import urlencode

import magic
import markupsafe
import pygments
from PIL import Image
from bottle import HTTPResponse
from bottle import request
from bottle import response
from bottle import static_file as bottle_static_file
from pygments.formatters import HtmlFormatter
from pygments.lexers import PhpLexer
from pygments.lexers import TextLexer
from pygments.lexers import get_all_lexers
from pygments.lexers import get_lexer_by_name
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound

from project import config
from project.configdefines import gallery_params


def get_session():
    return request.environ.get("beaker.session", {})


def id_generator(size=6, chars=string.ascii_letters + string.digits):
    """ Generates a random string of given size """
    return "".join(random.SystemRandom().choice(chars) for _ in range(size))


def strs_to_ints(dicts):
    """ Converts all strings which are ints in a dict to actual ints
        (for bottle GET/POST variables) """
    return {
        key: int(value) if value.isdigit() else value for key, value in dicts.items()
    }


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
        "https" if get_setting("ssl") else "http", request.environ.get("HTTP_HOST"),
    )


def static_file(path: str, root: str, filename: Optional[str] = None) -> HTTPResponse:
    file_path = os.path.join(root, path)
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
        return response

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


def key_password_return(session):
    # Check if the user has got their key and password stored, else
    # generate a mostly secure key for them.
    if session.get("id"):
        return {"key": session.get("key"), "password": session.get("password")}
    return {"key": id_generator(15), "password": id_generator(15)}
