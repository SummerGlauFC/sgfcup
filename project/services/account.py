import hashlib
import re
from functools import partial
from typing import Optional
from typing import Tuple

from flask import Response
from flask import request

from project import user_settings
from project import db
from project.constants import TypedDict
from project.functions import get_dict
from project.functions import json_error


class AccountInterface(TypedDict, total=False):
    id: int
    key: str
    password: str


ANONYMOUS_ACCOUNT = AccountInterface(id=0)
ACCOUNT_KEY_REGEX = "[a-zA-Z0-9_-]+"


class AccountService:
    @staticmethod
    def get_by_id(user_id: int) -> Optional[AccountInterface]:
        """
        Get a user by their ID.

        :param user_id: the ID of the user
        :return: row of the User if they exist
        """
        return db.select("accounts", where={"id": user_id}, singular=True)

    @staticmethod
    def get_by_key(key: str) -> Optional[AccountInterface]:
        """
        Get a user by their key.

        :param key: the key of the user
        :return: row of the User if they exist
        """
        return db.select("accounts", where={"key": key}, singular=True)

    @staticmethod
    def create(new_attrs: AccountInterface) -> AccountInterface:
        """
        Create an account with the given values.

        :param new_attrs: dict of values to use
        :return: the created account
        """
        account = db.insert("accounts", new_attrs)
        return AccountService.get_by_id(account.lastrowid)

    @staticmethod
    def update(user_id: int, new_attrs: AccountInterface):
        """
        Update an account with the given values.

        :param user_id: the ID of the user to update
        :param new_attrs: dict of values to use
        """
        db.update("accounts", new_attrs, {"id": user_id})

    @staticmethod
    def authenticate(
        key: str, password: str
    ) -> Tuple[Optional[AccountInterface], bool]:
        """
        Check if the given key/password authenticates an account.

        :param key: user key
        :param password: password of user
        :return: A tuple containing the user (if they exist), and a boolean indicating if they were authenticated
        """
        authenticated = False
        user = AccountService.get_by_key(key)
        if user:
            authenticated = user["password"] == password
        return user, authenticated

    @staticmethod
    def is_key_valid(key: str) -> bool:
        """
        Check if the given key is valid.

        :param key: key to validate
        :return: True if valid key, else False
        """
        return bool(re.match(f"^{ACCOUNT_KEY_REGEX}$", key))

    @staticmethod
    def get_or_create_account(key, password) -> Tuple[AccountInterface, bool]:
        """
        Get the specified account if it exists, else create it.

        :param key: account key
        :param password: account password
        :return: account matching the given credentials
        """
        if not key:
            # if no key is provided, anonymous login
            return ANONYMOUS_ACCOUNT, True

        # Keys must only contain alphanumerics and underscores/hyphens
        if not AccountService.is_key_valid(key):
            raise json_error(
                "Invalid key given. (can only contain letters, numbers, underscores and hyphens)"
            )

        # Check if the specified account already exists.
        user, is_authed = AccountService.authenticate(key, password)
        if not user:
            # create the user if they do not exist
            user = AccountService.create({"key": key, "password": password})
            is_authed = True

        return user, is_authed

    @staticmethod
    def get_settings(user_id: int):
        """
        Get settings for the specified user.

        :param user_id: the ID of the user to get settings for
        :return: settings for the given user
        """
        return user_settings.get_all_values(user_id)

    @staticmethod
    def get_auth_cookie(user_id: int) -> Optional[str]:
        """
        Get the gallery authentication cookie for the given user ID.

        :param user_id: user ID to get cookie for
        :return: hashed gallery password or None
        """
        return request.cookies.get(f"auth+{user_id}")

    @staticmethod
    def validate_auth_cookie(user_id: int, settings: Optional[dict] = None) -> bool:
        """
        Validate a gallery auth cookie for the given user.
        TODO: move to gallery service

        :param user_id: ID of the user
        :param settings: user settings dict (pass in if already grabbed)
        :return: True if the auth cookie is valid or not needed, else False
        """
        if not settings:
            settings = AccountService.get_settings(user_id)
        get_user_setting = partial(get_dict, settings)
        if get_user_setting("block.value") and get_user_setting(
            "gallery_password.value"
        ):
            auth_cookie = AccountService.get_auth_cookie(user_id)
            hex_pass = hashlib.sha1(
                get_user_setting("gallery_password.value").encode("utf-8")
            ).hexdigest()
            if not auth_cookie or not hex_pass == auth_cookie:
                return False
        return True

    @staticmethod
    def set_auth_cookie(
        resp: Response, user_id: int, authcode: str, remember: bool = False
    ):
        """
        Set a gallery auth cookie for the given user.
        TODO: move to gallery service

        :param resp: response to set cookies for
        :param user_id: ID of the user
        :param authcode: code to save in cookie for verification
        :param remember: if the cookie should be remembered
        """
        name = f"auth+{user_id}"
        value = hashlib.sha1(authcode.encode("utf-8")).hexdigest()
        if remember:
            resp.set_cookie(name, value, max_age=3600 * 24 * 7 * 30 * 12, path="/")
        else:
            resp.set_cookie(name, value, path="/")
