import random
import string
from PIL import Image
import config
from math import ceil
import markupsafe
import re


def id_generator(size=6, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def strs_to_ints(dicts):
    new = {}

    for key, value in dicts.iteritems():
        new[key] = int(value) if value.isdigit() else value

    return new


def is_image(path):
    try:
        im = Image.open(path)
    except IOError:
        return False
    return im


def highlight(text, search):
    output = ''
    i = 0
    text = markupsafe.escape(text)
    regex = re.compile(r"(" + re.escape(search) + ")", re.I)
    for m in regex.finditer(text):
        output += "".join([text[i:m.start()],
                           "<span class='hl'>",
                           text[m.start():m.end()],
                           "</span>"])
        i = m.end()
    return "".join([output, text[i:]])


def get_userid(key):
    userid = config.db.fetchone(
        "SELECT * FROM `accounts` WHERE `key` = %s", [key])

    if userid:
        return userid["id"]
    else:
        return False


def get_inrange(get, default, highest):
    if get:
        if int(get) in range(highest):
            return int(get)
        else:
            return default
    else:
        return default


def sizeof_fmt(num, short=None):
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.2f %s" % (num, x) if not short else "%3.0f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, 'TB')


class Pagination(object):

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
        return '{},{}'.format(self.per_page * (self.page - 1), self.per_page)

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=3, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
