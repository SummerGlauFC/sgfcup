import functools

from bottle import jinja2_template as template
from bottle import request

from project import app
from project import config
from project import functions
from project.functions import auth_account

SETTING_LINK = '<p><a href="/settings">Return to settings...</a></p>'
error = functools.partial(template, "error.tpl", extra=SETTING_LINK)


@app.route("/settings", method="GET")
def settings():
    SESSION = request.environ.get("beaker.session", {})

    return template(
        "settings.tpl",
        settings=config.user_settings.get_all_values(SESSION.get("id", 0)),
        key=SESSION.get("key"),
        password=SESSION.get("password"),
    )


@app.route("/settings", method="POST")
def settings_process():
    SESSION = request.environ.get("beaker.session", {})

    confirm_key = request.forms.get("confirm_key")
    confirm_password = request.forms.get("confirm_pass")
    change_password = request.forms.get("password")

    if not confirm_key or not confirm_password:
        return error(error="No key or password entered.")

    account = auth_account(confirm_key, confirm_password)
    if not account:
        return error(error="Key or password is incorrect.")

    key_password = account["password"]
    key_id = account["id"]

    SESSION["id"] = key_id
    SESSION["key"] = confirm_key
    SESSION["password"] = key_password

    if change_password:
        if key_password == change_password:
            return error(
                error="Password change ignored due to being the same as previous password."
            )
        config.db.update(
            "accounts", {"password": change_password}, {"key": confirm_key},
        )
        SESSION["password"] = change_password

    # Convert form strings to integers as HTTP likes to not
    # distinguish them.
    new_forms = functions.strs_to_ints(request.forms)

    # Use the PickleSettings class in order to update/set settings
    config.user_settings.set(SESSION["id"], new_forms)

    return template(
        "general.tpl",
        content="Your settings have been saved.",
        title="Success!",
        extra=SETTING_LINK,
    )
