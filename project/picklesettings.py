import json
from jsonmerge import merge
from db import DB
from pprint import pprint
import cPickle as pickle

class PickleSettings(object):

    ''' A class to handle the use of JSON for user settings. '''

    def __init__(self, json_file, db_instance):
        ''' expects to be called as such:
            test = JSONSettings("user_settings.json", db)
            where "user_settings.json" is the filename of the base config
            and db is an instance of db.DB '''

        with open(json_file) as f:
            self.json_file = json.load(f)

        self.db = db_instance

    def do(self, user_id, new_json, current_config=None):
        ''' handles the insertion of user info into the database '''

        if not current_config:
            current_config = self.db.fetchone(
                "SELECT * FROM `settings` WHERE userid = %s", [user_id])

        if current_config:
            if current_config["json"] != "0":
                #merged_json = json.dumps(merge(
                #    json.loads(current_config["json"]), json.loads(new_json)))

                merged_json = merge(pickle.loads(current_config["json"]), new_json)

                self.db.execute(
                    "UPDATE `settings` SET `json`=%s WHERE `userid`=%s", (pickle.dumps(merged_json, -1), user_id))
        else:
            self.db.insert("settings", {"userid": user_id, "json": pickle.dumps(new_json, -1)})

    def changeValues(self, values):
        ''' returns a dict which contains the users new value for an option '''

        temporary_json = {}
        for key, value in values.iteritems():
            if key in self.json_file:
                temporary_json[key] = {}
                if "options" in self.json_file[key]:
                    if value not in range(len(self.json_file[key]["options"])):
                        return False
                temporary_json[key]["value"] = value
        return temporary_json

    def _get(self, user_id):
        ''' returns a users config, including defaults. '''

        current_config = self.db.fetchone(
            "SELECT * FROM `settings` WHERE userid = %s", [user_id])

        if current_config:
            merged_json = merge(
                self.json_file, pickle.loads(current_config["json"]))
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

    def set(self, user_id, items):
        ''' sets multiple values at once (avoids multiple sql selects)
            expects to be called as such:
                set(user_id, items)
            where user_id is the id of a user from the `accounts` table
            and items is a dictionary of key: value
                like: {"ext": 0, "gallery_password": "test"} '''

        current_config = self.db.fetchone(
            "SELECT * FROM `settings` WHERE userid = %s", [user_id])

        self.do(user_id, self.changeValues(items),
                current_config)

    def get_all_values(self, user_id):
        jsoned = self._get(user_id)
        for key in jsoned:
            if "value" not in jsoned[key]:
                jsoned[key]["value"] = jsoned[key]["default"]

        return jsoned
