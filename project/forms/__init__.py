from typing import List

from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import Optional
from wtforms.widgets import PasswordInput

from project.functions import key_password_return


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

    key = StringField("User", validators=[Optional()])
    # allow password to be set/retrieved
    # TODO: remove once proper login implemented
    password = StringField(
        "Password", widget=PasswordInput(hide_value=False), validators=[Optional()]
    )
