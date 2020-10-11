import json
import pickle

from jsonmerge import merge


class PickleSettings:
    """ A class to handle the use of Pickle for user settings. """

    def __init__(self, json_file, db_instance):
        """ expects to be called as such:
                settings = PickleSettings('user_settings.json', db)
            where 'user_settings.json' is the filename of the base config
            and db is an instance of db.DB """

        with open(json_file) as f:
            self.json_file = json.load(f)

        self.db = db_instance

    def _get_config_blob(self, user_id):
        return self.db.select("settings", where={"userid": user_id}, singular=True)

    def _update(self, user_id, new_json, current_config=None):
        """ handles the insertion of user info into the database """

        # TODO: move from pickle to just json string

        if not current_config:
            current_config = self._get_config_blob(user_id)

        if current_config:
            if current_config["json"] != "0":
                merged_json = merge(pickle.loads(current_config["json"]), new_json)
                self.db.update(
                    "settings",
                    {"json": pickle.dumps(merged_json, -1)},
                    {"userid": user_id},
                )
        else:
            self.db.insert(
                "settings", {"userid": user_id, "json": pickle.dumps(new_json, -1)}
            )

    def change_values(self, values):
        """ returns a dict which contains the users new value for an option """

        temporary_json = {}
        for key, value in values.items():
            if key in self.json_file:
                temporary_json[key] = {}
                if "options" in self.json_file[key]:
                    if value not in range(len(self.json_file[key]["options"])):
                        return False
                temporary_json[key]["value"] = value
        return temporary_json

    def _get(self, user_id):
        """ returns a users config, including defaults. """

        current_config = self._get_config_blob(user_id)
        if current_config:
            # print current_config, dir(current_config)
            conf = pickle.loads(current_config["json"])

            # make sure removed config values are ignored
            new = {}
            for key in conf:
                if key in self.json_file:
                    new[key] = conf[key]

            merged_json = merge(self.json_file, new)
            return merged_json
        return self.json_file

    def get(self, user_id, key):
        """ gets a key from a users config, and returns the default option if
            the user has not set it yet. """

        conf = self._get(user_id)
        return conf[key].get("value", conf[key]["default"])

    def set(self, user_id, items):
        """ sets multiple values at once (avoids multiple sql selects)
            expects to be called as such:
                instance.set(user_id, items)
            where user_id is the id of a user from the `accounts` table
            and items is a dictionary of key: value
                like: {'ext': 0, 'gallery_password': 'test'} """

        current_config = self._get_config_blob(user_id)
        self._update(user_id, self.change_values(items), current_config)

    def get_all_values(self, user_id):
        """ returns all values from a users config, including defaults.
            Like a version of get for every key instead.
        """
        conf = self._get(user_id)
        for key in conf:
            if "value" not in conf[key] and "default" in conf[key]:
                conf[key]["value"] = conf[key]["default"]
        return conf
