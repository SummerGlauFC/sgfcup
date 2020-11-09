import functools
import operator

from flask import Blueprint
from flask import flash
from flask import render_template
from flask_login import current_user
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import RadioField
from wtforms import StringField
from wtforms.validators import EqualTo
from wtforms.validators import Optional

from project.extensions import user_settings
from project.services.account import AccountInterface
from project.services.account import AccountService
from project.usersettings import SettingsJson

blueprint = Blueprint("settings", __name__)


def make_settings_form(settings: SettingsJson, **kwargs):
    class SettingsForm(FlaskForm):
        new_password = PasswordField(
            "New password",
            validators=[
                Optional(),
                EqualTo("confirm_new_password", message="Passwords must match"),
            ],
        )
        confirm_new_password = PasswordField(
            "Confirm password", validators=[Optional(), EqualTo("new_password")]
        )

    # flatten the settings groups to just a list of the fields
    # because we dont care about the groups for form generation
    for item in functools.reduce(operator.iconcat, settings["groups"].values(), []):
        setting = settings[item]
        if setting["type"] == "radio":
            choices = enumerate(setting["options"])
            field = RadioField(
                setting["name"],
                default=setting["default"],
                choices=choices,
                coerce=int,
            )
        else:
            field = StringField(setting["name"], default=setting["default"])
        setattr(SettingsForm, item, field)

    return SettingsForm(data=user_settings.get_only_values(settings), **kwargs)


def flash_update_error(field=None, err=None):
    flash("There was a problem saving your settings.", "error")
    if field and err:
        field.errors.append(err)


@blueprint.route("/settings", methods=["GET", "POST"])
@login_required
def settings_view():
    settings = AccountService.get_settings(current_user.get_id())
    form = make_settings_form(settings)

    def render_form():
        return render_template("settings.tpl", settings=settings, form=form)

    if form.is_submitted():
        if not form.validate():
            flash_update_error()
            return render_form()

        new_password = form.new_password.data
        if new_password:
            if current_user["password"] == new_password:
                flash_update_error(form.new_password, "Same as current password")
                return render_form()
            AccountService.update(
                current_user.get_id(), AccountInterface(password=new_password)
            )

        # Use the UserSettings class in order to update/set settings
        user_settings.set(current_user.get_id(), form.data)
        flash("Success! Your settings have been saved.")
    return render_form()
