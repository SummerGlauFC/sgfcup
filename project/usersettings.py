import json
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import TypedDict
from typing import Union

from jsonmerge import merge

import db


def dump_json(obj):
    return json.dumps(obj, separators=(",", ":"))


class SettingsRow(TypedDict):
    id: int
    userid: int
    json: str


SettingValue = Union[str, int]
SettingChangeValue = Dict[str, SettingValue]


class SettingsValue(TypedDict, total=False):
    value: SettingValue


class Setting(SettingsValue, total=False):
    name: str
    notes: str
    type: Literal["text", "radio"]
    options: List[str]
    default: SettingValue


SettingsJson = Dict[str, Setting]
SettingsValueJson = Dict[str, SettingsValue]


class UserSettings:
    """ A class to handle user settings. """

    def __init__(self, settings_file: str, db_instance: db.DB):
        """
        Handle user settings given a settings file and a database instance.

        :param settings_file: json file specifying user settings
        :param db_instance: instance of :py:class:`db.DB`
        """
        with open(settings_file) as f:
            self.settings: SettingsJson = json.load(f)

        self.db = db_instance

    def _get_settings_row(self, user_id) -> Optional[SettingsRow]:
        """
        Get the settings row for the given user.

        :param user_id: the ID of the user
        :return: settings row if it exists, else None
        """
        return self.db.select("settings", where={"userid": user_id}, singular=True)

    def _update(
        self, user_id: int, data: SettingsValueJson, curr_settings: SettingsRow = None
    ):
        """
        Update or insert the new settings for the given user.

        :param user_id: the ID of the user
        :param data: the new data
        :param curr_settings: the current settings row if already present
        """
        if not curr_settings:
            curr_settings = self._get_settings_row(user_id)

        if curr_settings:
            if curr_settings["json"] != "0":
                merged_json = merge(json.loads(curr_settings["json"]), data)
                self.db.update(
                    "settings",
                    {"json": dump_json(merged_json)},
                    {"userid": user_id},
                )
        else:
            self.db.insert("settings", {"userid": user_id, "json": dump_json(data)})

    def _change_values(self, values: SettingChangeValue) -> SettingsValueJson:
        """
        Generate a dict which contains only the values for the corresponding settings.

        :param values: dict of {setting: value}
        :return: dict of {setting: {value: value}}
        """
        out = {}
        for key, value in values.items():
            if key in self.settings:
                setting = self.settings[key]
                if "options" in setting:
                    if value not in range(len(setting["options"])):
                        # use default option if invalid is provided
                        value = setting["default"]
                out[key] = SettingsValue(value=value)
        return out

    def _get(self, user_id) -> SettingsJson:
        """
        Get a users settings. Includes default values if not set.

        :param user_id: the ID of the user
        :return: the users settings including defaults
        """
        current_config = self._get_settings_row(user_id)
        if current_config:
            conf = json.loads(current_config["json"])
            # make sure only existing keys are given
            new: SettingsJson = {key: conf[key] for key in conf if key in self.settings}
            # merge the users settings into the defaults
            return merge(self.settings, new)
        return self.settings

    def get(self, user_id: int, key: str) -> SettingValue:
        """
        Get a given key from the users settings. Return the default option if not set.

        :param user_id: the ID of the user
        :param key: the setting to get
        :return: setting value if it exists, else the default value
        """
        conf = self._get(user_id)
        return conf[key].get("value", conf[key]["default"])

    def set(self, user_id: int, items: SettingChangeValue):
        """
        Set multiple settings for a user.

        :param user_id: the ID of the user
        :param items: dict of {setting: value}
        """
        current_config = self._get_settings_row(user_id)
        self._update(user_id, self._change_values(items), current_config)

    def get_all_values(self, user_id) -> SettingsJson:
        """returns all values from a users config, including defaults.
        Like a version of get for every key instead.
        """
        conf = self._get(user_id)
        for key in conf:
            if "value" not in conf[key] and "default" in conf[key]:
                conf[key]["value"] = conf[key]["default"]
        return conf
