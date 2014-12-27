import json
from jsonmerge import merge
from db import DB


class JSONSettings(object):

    ''' A class to handle the use of JSON for user settings. '''

    def __init__(self, json_file, db_instance):
        ''' expects to be called as such:
            test = JSONSettings("user_settings.json", db)
            where "user_settings.json" is the filename of the base config
            and db is an instance of db.DB '''

        with open(json_file) as f:
            self.json_file = json.load(f)

        self.db = db_instance

    def do(self, user_id, new_json):
        ''' handles the insertion of user info into the database '''

        current_config = self.db.execute(
            "SELECT * FROM `settings` WHERE userid = %s", [user_id])

        if current_config:
            merged_json = merge(current_config["json"], new_json)

            self.db.execute(
                "UPDATE `settings` SET `json`=%s WHERE `userid`=%s", [merged_json, user_id])
        else:
            self.db.insert("settings", {"json": new_json, "userid": user_id})

    def changeValues(self, key, value):
        ''' returns a dict which contains the users new value for an option '''

        temporary_json = {}

        if key in self.json_file:
            temporary_json[key] = {}
            if "options" in self.json_file[key]:
                if value not in range(len(self.json_file[key]["options"])):
                    return False
            temporary_json[key]["value"] = value
            return temporary_json
        else:
            return False

    def _get(self, user_id):
        ''' returns a users config, including defaults. '''

        current_config = self.db.execute(
            "SELECT * FROM `settings` WHERE userid = %s", [user_id])

        print dir(current_config), current_config.rowcount

        if current_config.rowcount != -1:
            merged_json = merge(self.json_file, current_config["json"])
            return merged_json
        else:
            return self.json_file

    def get(self, user_id, key):
        ''' gets a key from a users config, and returns the default option if
            the user has not set it yet. '''

        user_json = self._get(user_id)

        if "value" in user_json[key]:
            return user_json[key]["value"]
        else:
            return user_json[key]["default"]

    def set(self, user_id, key, value):
        ''' sets a value for a config key. '''

        self.do(user_id, self.changeValues(key, value))

    def get_all_values(self, user_id):
        jsoned = self._get(user_id)
        for key in jsoned:
            if "value" not in jsoned[key]:
                jsoned[key]["value"] = jsoned[key]["default"]

        return jsoned