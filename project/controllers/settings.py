import functools
import operator

from flask import flash
from flask import render_template
from flask import session
from wtforms import PasswordField
from wtforms import RadioField
from wtforms import StringField
from wtforms.validators import Optional

from project import app
from project import user_settings
from project.forms import LoginForm
from project.services.account import AccountInterface
from project.services.account import AccountService
from project.usersettings import SettingsJson


def make_settings_form(settings: SettingsJson, **kwargs):
    class SettingsForm(LoginForm):
        new_password = PasswordField("New password", validators=[Optional()])

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


@app.route("/settings", methods=["GET", "POST"])
def settings_get():
    settings = AccountService.get_settings(session.get("id", 0))
    form = make_settings_form(settings)

    def render_form():
        return render_template("settings.tpl", settings=settings, form=form)

    if form.is_submitted():
        if not form.validate():
            flash_update_error()
            return render_form()

        key = form.key.data
        password = form.password.data
        user, is_authed = AccountService.authenticate(key, password)
        if not user or not is_authed:
            flash_update_error(form.key, "Key or password is incorrect")
            return render_form()

        key_id = user["id"]
        key_password = user["password"]

        session["id"] = key_id
        session["key"] = key
        session["password"] = key_password

        new_password = form.new_password.data
        if new_password:
            if key_password == new_password:
                flash_update_error(form.new_password, "Same as current password")
                return render_form()
            AccountService.update(key_id, AccountInterface(password=new_password))
            session["password"] = new_password

        # Use the UserSettings class in order to update/set settings
        user_settings.set(session["id"], form.data)

        flash("Success! Your settings have been saved.")

    return render_form()
