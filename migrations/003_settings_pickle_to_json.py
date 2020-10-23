import os
import pickle

from migrations import db
from migrations import logger
from migrations import make_database_backup
from project.usersettings import dump_json

make_database_backup(os.path.basename(__file__))

for settings in db.select("settings"):
    if settings:
        json = settings["json"]
        if json != "0":
            user = settings["userid"]
            try:
                data = pickle.loads(json)
                new = dump_json(data)
                db.update("settings", {"json": new}, {"id": settings["id"]})
                logger.info(f"Updated settings for user id: {user}")
            except pickle.UnpicklingError:
                logger.info(f"Already migrated settings for user id: {user}")
