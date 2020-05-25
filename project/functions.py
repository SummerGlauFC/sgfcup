from __future__ import absolute_import, division, print_function

import functools
import inspect
import random
import re
import string
from builtins import range
from functools import partial
from math import ceil

import markupsafe
import pygments
from PIL import Image
from project import config
from pygments.formatters import HtmlFormatter
from pygments.lexers import (
    PhpLexer,
    TextLexer,
    get_all_lexers,
    get_lexer_by_name,
    get_lexer_for_filename,
    get_lexer_for_mimetype,
    guess_lexer,
)
from pygments.util import ClassNotFound


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


def hl(text, search):
    """ Use regex to highlight all occurances of a substring in a string """
    if not search:
        return text

    output = ""
    i = 0
    text = markupsafe.escape(text)
    regex = re.compile(r"(" + re.escape(search) + ")", re.I)
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
    else:
        return False


def get_inrange(get, default, highest):
    """ Checks if an int is in a range """
    if get:
        if int(get) in range(highest):
            return int(get)
        else:
            return default
    else:
        return default


def sizeof_fmt(num, short=None):
    """ Bytes to a human-readable format """
    for x in ["bytes", "KB", "MB", "GB"]:
        if num < 1024.0 and num > -1024.0:
            return "%3.2f %s" % (num, x) if not short else "%3.0f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, "TB")


class Pagination(object):

    """ Useful pagination class """

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

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
                or (
                    num > self.page - left_current - 1
                    and num < self.page + right_current
                )
                or num > self.pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num


LANGUAGES = get_all_lexers()


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
    if alias in LANGUAGES:
        return alias
    try:
        lexer = get_lexer_by_name(alias)
    except ClassNotFound:
        return default
    return get_known_alias(lexer)


def get_known_alias(lexer, default="text"):
    """Return the known alias for the lexer."""
    for alias in lexer.aliases:
        if alias in LANGUAGES:
            return alias
    return default


def list_languages():
    """List all languages."""
    languages = LANGUAGES.items()
    languages.sort(key=lambda x: x[1].lstrip(" _-.").lower())
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
    formatter = HtmlFormatter(linenos=_linenos, cssclass="syntax", style="vs")
    return f'<div class="syntax">{pygments.highlight(code, lexer, formatter)}</div>'


def css(style="vs", css_class=".syntax"):
    """ Gets the CSS for pygments """
    return HtmlFormatter(style=style).get_style_defs(css_class)


def json_error(error):
    return {"success": False, "error": error}


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
