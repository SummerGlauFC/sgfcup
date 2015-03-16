from db import DB
import shutil
import sys
import os
import glob

Settings = {
    "database": {
        "user": sys.argv[1],
        "password": sys.argv[2],
        "db_dest": sys.argv[3]
    },
    "dest_dir": "/var/www/sgfcup_dev/img/p/"
}

db = DB(user=Settings['database']['user'], password=Settings['database']
        ['password'], database=Settings['database']['db_dest'])

files = glob.glob('../bottleimg/img/p/*.*')

for file in files:
    f = os.path.basename(file)
    result = db.fetchall(
        'SELECT * FROM `files` WHERE `shorturl` = %s', [f.split('.')[0]])
    if result:
        for res in result:
            db.execute('UPDATE `files` SET `size`=%s WHERE `id` = %s',
                       [os.path.getsize(file), res['id']])
            # print "{} - {} ({})".format(f, res['original'],
            # os.path.getsize(file))


pastes = db.fetchall('SELECT * FROM `files` WHERE `ext` = "paste"', [])
if pastes:
    for res in pastes:
        paste = db.fetchone(
            'SELECT * FROM `pastes` WHERE `id` = %s', [res["original"]])
        db.execute('UPDATE `files` SET `size`=%s WHERE `id` = %s',
                   [len(paste["content"]), res['id']])
