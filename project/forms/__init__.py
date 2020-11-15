from typing import List

from flask import flash
from flask import url_for
from flask_login import login_user
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms.validators import InputRequired
from wtforms.validators import Optional
from wtforms.widgets import PasswordInput

from project.functions import Error
from project.functions import key_password_return
from project.functions import redirect_next
from project.services.account import AccountService


def flatten_errors(errors) -> List[str]:
    output = []
    for field, errors in errors.items():
        for error in errors:
            output.append(f"{field}: {error}")
    return output


class FlashErrorsForm(FlaskForm):
    """ Form which can flash its errors """

    def flash_errors(self):
        """ Flash form errors using flask.flash(). """
        errors = flatten_errors(self.errors)
        for error in errors:
            flash(error, "error")


class LoginForm(FlashErrorsForm):
    """ Form for logging in. Prefills with session information. """

    def __init__(self, **kwargs):
        kwargs["data"] = kwargs.get("data") or {}
        kwargs["data"].update(key_password_return())

        super().__init__(**kwargs)

    key = StringField("User", validators=[InputRequired()])

    # allow password to be set
    password = StringField(
        "Password",
        widget=PasswordInput(hide_value=False),
        validators=[InputRequired()],
    )

    link = SubmitField("Link Accounts", validators=[Optional()])

    def get_or_create_account(self):
        try:
            user, is_authed = AccountService.get_or_create_account(
                self.key.data, self.password.data
            )
            if not user or not is_authed:
                self.key.errors.append("Key or password is incorrect")
        except Error as e:
            self.key.errors.append(e.error)
            return None, False
        return user, is_authed

    @staticmethod
    def login(user):
        login_user(user)
        redirect_next(default=url_for("static.index"))
