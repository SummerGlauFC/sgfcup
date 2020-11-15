from typing import Optional

from project.services.account import AccountInterface
from project.services.account import AccountService


class OAuthService:
    @staticmethod
    def get_potential_name(userinfo, errors=None):
        """
        Get the potential account name for the given openid userinfo.

        :param userinfo: openid userinfo
        :param errors: list of errors to append to
        :return: tuple of (name, errors)
        """
        if not errors:
            errors = []
        subject = userinfo["sub"]
        potential_name = userinfo.get("preferred_username", subject)
        existing_user = AccountService.get_by_key(potential_name)
        if existing_user:
            # user with potential name exists already, use subject instead
            errors.append(
                f'User "{potential_name}" already exists, please authenticate as them or choose another username'
            )
            potential_name = subject

        # trim to 30 chars to fit in db
        # TODO: update key/password db length?
        potential_name = potential_name[:30]
        return potential_name, errors

    @staticmethod
    def link(user_id: int, subject: Optional[str]):
        """
        Link the given account to the given openid subject

        :param user_id: user ID to link
        :param subject: openid subject to link to the account
        :return:
        """
        AccountService.update(user_id, AccountInterface(hash=subject))
