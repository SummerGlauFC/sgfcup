from project import app, config, functions
from bottle import template, request, response
import hashlib
import os
from .view import api_thumb
from .upload import api_upload_file


def get_puush_user(hash):
    return config.db.fetchone(
        'SELECT * FROM `accounts` WHERE `hash`=%s', [hash])


# puush api integration
@app.route('/api/auth', method='POST')
def puush_auth():
    key = request.forms.get('e', '')
    password = request.forms.get('p', '')
    hash = request.forms.get('k', '')

    user = config.db.fetchone(
        'SELECT * FROM `accounts` WHERE `key`=%s', [key])

    if not hash:
        hash = hashlib.md5(key + password).hexdigest()

    # If it does, check their password OR hash is correct.
    if not user:
        # If the account doesn't exist, make a new account.
        new_account = config.db.insert(
            'accounts', {"key": key,
                         "password": password,
                         "hash": hash
                         }
        )
        user = config.db.fetchone(
            'SELECT * FROM `accounts` WHERE `id`=%s', [new_account.lastrowid])

    if (user["password"] == password or user["hash"] == hash):
        if user and not user["hash"]:
            config.db.execute("UPDATE `accounts` SET `hash`=%s WHERE `id`=%s",
                              [hash, user["id"]])

        return "1,{},,0".format(hash)

    return '-1'


@app.route('/api/up', method='POST')
def puush_up():
    user = get_puush_user(request.forms.get('k', ''))

    if user:
        return api_upload_file('file', {
            "key": user["key"],
            "password": user["password"],
            "file": request.files.get('f', '')
        }, puush=True)

    print 'we fucked up'
    return '-1'


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
                    id=row["id"], date=row["date"].strftime('%Y-%m-%d %H:%M:%S'),
                    url="{}://{}/{}".format(protocol, host, row["shorturl"]),
                    original=row["original"].replace(',', '_'), hits=row["hits"])

                ret += "{id},{date},{url},{original},{hits},0\n".format(**formats)

        return ret

    return '-1'

@app.route('/api/del', method='POST')
def puush_del():
    i = request.forms.get('i', '')

    user = get_puush_user(request.forms.get('k', ''))

    f = config.db.fetchone(
        'SELECT * FROM `files` WHERE `id`=%s', [i])

    if f["userid"] == user["id"]:
        try:
            delete_query = config.db.execute(
                "DELETE FROM `files` WHERE `id` = %s", [i])

            os.remove(config.Settings["directories"]
                      ["files"] + f["shorturl"] + f["ext"])
        except:
            return '-1'

        return puush_hist()

    return '-1'


@app.route('/api/thumb', method='POST')
def puush_del():
    user = get_puush_user(request.forms.get('k', ''))

    f = config.db.fetchone(
        'SELECT * FROM `files` WHERE `id`=%s', [request.forms.get('i', '')])

    if f["userid"] == user["id"]:
        try:
            return api_thumb(f["shorturl"], temp=True, size=(100, 100))
        except:
            return '-1'

    return '-1'
