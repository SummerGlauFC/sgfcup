import functools

from flask import render_template
from flask import request
from flask import session

from project import app
from project import user_settings
from project.services.account import AccountInterface
from project.services.account import AccountService

SETTING_LINK = '<p><a href="/settings">Return to settings...</a></p>'
error = functools.partial(render_template, "error.tpl", extra=SETTING_LINK)


@app.route("/settings", methods=["GET"])
def settings():
    return render_template(
        "settings.tpl",
        settings=AccountService.get_settings(session.get("id", 0)),
        key=session.get("key"),
        password=session.get("password"),
    )


@app.route("/settings", methods=["POST"])
def settings_process():
    confirm_key = request.form.get("confirm_key")
    confirm_password = request.form.get("confirm_pass")
    change_password = request.form.get("password")

    if not confirm_key or not confirm_password:
        return error(error="No key or password entered.")

    user, is_authed = AccountService.authenticate(confirm_key, confirm_password)
    if not user:
        return error(error="Key or password is incorrect.")

    key_password = user["password"]
    key_id = user["id"]

    session["id"] = key_id
    session["key"] = confirm_key
    session["password"] = key_password

    if change_password:
        if key_password == change_password:
            return error(
                error="Password change ignored due to being the same as previous password."
            )
        AccountService.update(user["id"], AccountInterface(password=change_password))
        session["password"] = change_password

    # Convert form strings to integers as HTTP likes to not
    # distinguish them.
    new_forms = {
        key: request.form.get(key, type=user_settings.get_setting_type(key))
        for key in request.form.keys()
    }

    # Use the UserSettings class in order to update/set settings
    user_settings.set(session["id"], new_forms)

    return render_template(
        "general.tpl",
        content="Your settings have been saved.",
        title="Success!",
        extra=SETTING_LINK,
    )
