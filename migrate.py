from db import DB
import shutil
import sys

Settings = {
    "database": {
        "user": sys.argv[1],
        "password": sys.argv[2],
        "db_source": sys.argv[3],
        "db_dest": sys.argv[4]
    },
    "source_dir": "/var/www/bottleimg/img/p/",
    "dest_dir": "/var/www/sgfcup_dev/img/p/"
}

db_source = DB(user=Settings['database']['user'], password=Settings['database']
               ['password'], database=Settings['database']['db_source'])

db_dest = DB(user=Settings['database']['user'], password=Settings['database']
             ['password'], database=Settings['database']['db_dest'])


unique_accounts = db_source.fetchall(
    "SELECT DISTINCT `key`,`passs` FROM `keys`")

for account in unique_accounts:
    account_exists = db_dest.fetchone(
        'SELECT * FROM `accounts` where `key` = %s', [account["key"]])

    if account_exists:
        if account_exists["password"] != account["passs"]:
            db_dest.execute(
                'UPDATE `accounts` SET `password` = %s WHERE `key` = %s',
                [account["passs"], account["key"]])
        account_id = account_exists["id"]
    else:
        account_id = db_dest.insert('accounts',
                                    {"key": account["key"],
                                     "password": account["passs"]}).lastrowid

    print 'ACCOUNT: `%s` into new db.' % account_id

    account_uploads = db_source.fetchall(
        "SELECT * FROM `keys` WHERE `key` = %s AND `passs` = %s",
        [account["key"], account["passs"]])

    for upload in account_uploads:
        if upload["is_paste"] == 'y' or upload["is_paste"] == 1:
            paste = db_dest.insert('pastes',
                                   {"userid": account_id, "shorturl": upload["shorturl"],
                                    "name": upload["url"], "lang": upload["paste_lang"],
                                       "content": upload["original"]})

            db_dest.insert('files',
                           {"userid": account_id, "shorturl": upload["shorturl"],
                            "ext": "paste", "original": paste.lastrowid,
                            "hits": upload["hits"]})
        else:
            ext = '.' + upload["url"].split('.')[-1]
            print 'Could not copy `%s` to `%s`' % (Settings["source_dir"] + upload["url"], Settings["dest_dir"])

            db_dest.insert('files', {"userid": account_id, "shorturl": upload[
                           "shorturl"], "ext": ext, "original": upload["original"], "hits": upload["hits"]})

        print 'UPLOAD: `%s` into new db.' % upload["shorturl"]
