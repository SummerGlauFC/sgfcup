from project import app, config, functions
from bottle import template, request, response
import hashlib
import os
from .view import api_thumb
from .upload import api_upload_file


# puush api integration
@app.route('/api/auth', method='POST')
def puush_auth():
    key = request.forms.get('e', '')
    password = request.forms.get('p', '')
    hash = request.forms.get('k', '')

    user = config.db.fetchone(
        'SELECT * FROM `accounts` WHERE `key`=%s', [key])

    hash = hash if hash else hashlib.md5(key + password).hexdigest()
    print 'key: {}, password: {}, hash: {}'.format(key, password, hash)

    is_authed = False

    # If it does, check their password OR hash is correct.
    if user:
        is_authed = (user["password"] == password or user["hash"] == hash)
        user_id = user["id"]
    else:
        # If the account doesn't exist, make a new account.
        new_account = config.db.insert(
            'accounts', {"key": key,
                         "password": password,
                         "hash": hash
                         }
        )
        user_id = new_account.lastrowid
        is_authed = True

    if is_authed:
        user = config.db.fetchone(
            'SELECT * FROM `accounts` WHERE `id`=%s', [user_id])

        if user and not user["hash"]:
            config.db.execute("UPDATE `accounts` SET `hash`=%s WHERE `id`=%s",
                              [hash, user_id])

        return "1,{},,0".format(hash)
    else:
        return '-1'


@app.route('/api/up', method='POST')
def puush_up():
    k = request.forms.get('k', '')
    f = request.files.get('f', '')

    print k, request.forms.get('c', '')

    user = config.db.fetchone(
        'SELECT * FROM `accounts` WHERE `hash`=%s', [k])

    if user:
        return api_upload_file('file', {
            "key": user["key"], "password": user["password"], "file": f}, puush=True)
    else:
        print 'we fucked up'
        return '-1'


@app.route('/api/hist', method='POST')
def puush_hist():
    k = request.forms.get('k', '')

    user = config.db.fetchone(
        'SELECT * FROM `accounts` WHERE `hash`=%s', [k])

    ret = "0\n"
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


@app.route('/api/del', method='POST')
def puush_del():
    k = request.forms.get('k', '')
    i = request.forms.get('i', '')

    user = config.db.fetchone(
        'SELECT * FROM `accounts` WHERE `hash`=%s', [k])

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
    else:
        return '-1'


@app.route('/api/thumb', method='POST')
def puush_del():
    k = request.forms.get('k', '')
    i = request.forms.get('i', '')

    user = config.db.fetchone(
        'SELECT * FROM `accounts` WHERE `hash`=%s', [k])

    f = config.db.fetchone(
        'SELECT * FROM `files` WHERE `id`=%s', [i])

    if f["userid"] == user["id"]:
        try:
            return api_thumb(f["shorturl"], temp=True, size=(100, 100))
        except:
            return '-1'
    else:
        return '-1'
