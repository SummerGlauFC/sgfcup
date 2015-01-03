from project import app, functions, config
from bottle import static_file, request
from bottle import jinja2_view as view, jinja2_template as template


@app.route('/settings', method='GET')
def settings_view():
    SESSION = request.environ.get('beaker.session')

    settings = config.user_settings.get_all_values(SESSION.get("id", 0))
    return template("settings.tpl", settings=settings, key=SESSION.get("key"), password=SESSION.get("password"))


@app.route('/settings', method='POST')
@view("general.tpl")
def settings_process():
    SESSION = request.environ.get("beaker.session")

    confirm_key = request.forms.get('confirm_key')
    confirm_password = request.forms.get('confirm_pass')
    change_password = request.forms.get('password')

    message = ''
    title = ''

    if not confirm_key or not confirm_password:
        return {
            "message": "You didn't enter your key or password for confirmation.",
            "title": "Error"
        }
    else:
        account = config.db.fetchone(
            "SELECT * FROM `accounts` WHERE `key` = %s", [confirm_key])

        if account:
            key_password = account["password"]
            key_id = account["id"]

            if confirm_password == key_password:
                if key_id != SESSION.get('id'):
                    SESSION["id"] = key_id
                    SESSION["key"] = confirm_key
                    SESSION["password"] = key_password

                if change_password:
                    if key_password != change_password:
                        config.db.execute("UPDATE `accounts` SET `password` = %s WHERE `key` = %s", [change_password, confirm_key])

                        SESSION["id"] = account["id"]
                        SESSION["key"] = confirm_key
                        SESSION["password"] = change_password
                    else:
                        message = "Password change ignored due to being the same as previous password."
                        title = "Error"
            else:
                message = "Key or password is incorrect.",
                title = "Error"

            new_forms = functions.strs_to_ints(request.forms)
            config.user_settings.set(SESSION["id"], new_forms)
        else:
            message = "Account does not exist.",
            title = "Error"

    return {
        "message": "Your settings have been set" if not message else message,
        "title": "Success!" if not title else title
    }
