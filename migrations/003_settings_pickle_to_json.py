import pickle

from project.config import db
from project.usersettings import dump_json

for settings in db.select("settings"):
    if settings:
        if settings["json"] != "0":
            try:
                data = pickle.loads(settings["json"])
                new = dump_json(data)
                db.update("settings", {"json": new}, {"id": settings["id"]})
                print(f"Updated settings for user ID {settings['userid']}")
            except pickle.UnpicklingError:
                print(f"Already migrated settings for user ID {settings['userid']}")
