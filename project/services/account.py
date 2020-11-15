import re
from collections import UserDict
from typing import Optional
from typing import Tuple

from flask_login import AnonymousUserMixin
from flask_login import UserMixin

from project import db
from project.constants import TypedDict
from project.extensions import user_settings
from project.functions import json_error


class AccountInterface(TypedDict, total=False):
    id: int
    key: str
    password: str
    hash: Optional[str]


class Account(UserMixin, UserDict):
    data: AccountInterface

    def get_id(self):
        return self.data["id"]


class AnonymousAccount(AnonymousUserMixin, UserDict):
    data: AccountInterface

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(id=0, key="anon")

    def get_id(self):
        return self.data["id"]


ANONYMOUS_ACCOUNT = AnonymousAccount()
ACCOUNT_KEY_REGEX = "[a-zA-Z0-9_-]+"


class AccountService:
    @staticmethod
    def get_by_id(user_id: int) -> Optional[Account]:
        """
        Get a user by their ID.

        :param user_id: the ID of the user
        :return: row of the User if they exist
        """
        acc = db.select("accounts", where={"id": user_id}, singular=True)
        if acc:
            return Account(**acc)
        return None

    @staticmethod
    def get_by_key(key: str) -> Optional[Account]:
        """
        Get a user by their key.

        :param key: the key of the user
        :return: row of the User if they exist
        """
        acc = db.select("accounts", where={"key": key}, singular=True)
        if acc:
            return Account(**acc)
        return None

    @staticmethod
    def get_by_subject(openid_subject: str) -> Optional[Account]:
        """
        Get a user by their openid subject.

        :param openid_subject: the subject of the user
        :return: row of the User if they exist
        """
        acc = db.select("accounts", where={"hash": openid_subject}, singular=True)
        if acc:
            return Account(**acc)
        return None

    @staticmethod
    def create(new_attrs: AccountInterface) -> Account:
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
    def authenticate(key: str, password: str) -> Tuple[Optional[Account], bool]:
        """
        Check if the given key/password authenticates an account.

        :param key: user key
        :param password: password of user
        :return: A tuple containing the user (if they exist), and a boolean indicating if they were authenticated
        """
        authenticated = False
        user = AccountService.get_by_key(key)
        if user:
            # do not authenticate the anon user
            if user["id"] == 0:
                return user, False
            authenticated = user["password"] == password
        return user, authenticated

    @staticmethod
    def is_key_valid(key: str) -> bool:
        """
        Check if the given key is valid.

        :param key: key to validate
        :return: True if valid key, else False
        """
        return key != "anon" and bool(re.match(f"^{ACCOUNT_KEY_REGEX}$", key))

    @staticmethod
    def get_or_create_account(key, password) -> Tuple[Account, bool]:
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
