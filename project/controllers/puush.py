from __future__ import division, print_function, absolute_import
from project import app, config
from bottle import request
import hashlib
import os
from .view import api_thumb
from .upload import api_upload_file


PUUSH_ERROR = config.PUUSH_ERROR


def get_puush_user(apikey):
    return config.db.select('accounts', where={"hash": apikey}, singular=True)

# puush api integration


@app.route('/api/auth', method='POST')
def puush_auth():
    key = request.forms.get('e', '')
    password = request.forms.get('p', '')
    apikey = request.forms.get('k', '')

    user = config.db.select('accounts', where={"key": key}, singular=True)

    if not apikey:
        apikey = hashlib.md5(key + password).hexdigest()

    # If it does, check their password OR hash is correct.
    if not user:
        # If the account doesn't exist, make a new account.
        new_account = config.db.insert(
            'accounts', {"key": key,
                         "password": password,
                         "hash": apikey
                         }
        )
        user = config.db.select(
            'accounts', where={"id": new_account.lastrowid}, singular=True)

    if (user["password"] == password or user["hash"] == apikey):
        if user and not user["hash"]:
            config.db.update('accounts', {"hash": apikey}, {"id": user["id"]})

        return "1,{},,0".format(apikey)

    return PUUSH_ERROR


@app.route('/api/up', method='POST')
def puush_up():
    user = get_puush_user(request.forms.get('k', ''))

    if user:
        return api_upload_file('file', {
            "key": user["key"],
            "password": user["password"],
            "file": request.files.get('f', '')
        }, puush=True)

    return PUUSH_ERROR


@app.route('/api/hist', method='POST')
def puush_hist():
    user = get_puush_user(request.forms.get('k', ''))

    ret = "0\n"
    if user:
        res = config.db.fetchall(
            'SELECT * FROM `files` WHERE `userid` = %s ORDER BY `date` DESC LIMIT 10', user["id"])

        protocol = 'http'

        if request.environ.get('HTTP_HOST') == "puush.me":
            host = config.Settings['directories']['url']
        else:
            host = request.environ.get('HTTP_HOST')

        if res:
            for row in res:
                formats = dict(
                    id=row["id"], date=row["date"].strftime(
                        '%Y-%m-%d %H:%M:%S'),
                    url="{}://{}/{}".format(protocol, host, row["shorturl"]),
                    original=row["original"].replace(',', '_'), hits=row["hits"])

                ret += "{id},{date},{url},{original},{hits},0\n".format(
                    **formats)

        return ret

    return PUUSH_ERROR


@app.route('/api/del', method='POST')
def puush_del():
    i = request.forms.get('i', '')

    user = get_puush_user(request.forms.get('k', ''))

    f = config.db.select('files', where={"id": i}, singular=True)

    if f["userid"] == user["id"]:
        try:
            config.db.delete('files', {"id": i})

            os.remove(config.Settings["directories"]
                      ["files"] + f["shorturl"] + f["ext"])
        except:
            return PUUSH_ERROR

        return puush_hist()

    return PUUSH_ERROR


@app.route('/api/thumb', method='POST')
def puush_thumb():
    user = get_puush_user(request.forms.get('k', ''))

    f = config.db.select(
        'files', where={"id": request.forms.get('i', '')}, singular=True)

    if f["userid"] == user["id"]:
        try:
            return api_thumb(f["shorturl"], temp=True, size=(100, 100))
        except:
            return PUUSH_ERROR

    return PUUSH_ERROR
