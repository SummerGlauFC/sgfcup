import hashlib
from functools import partial
from typing import Optional

from flask import Response
from flask import request

from project.functions import get_dict
from project.services.account import AccountService


class GalleryService:
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
            auth_cookie = GalleryService.get_auth_cookie(user_id)
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
