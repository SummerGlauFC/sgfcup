from project import app, functions, config
from bottle import static_file, request
from bottle import jinja2_view as view, jinja2_template as template


@app.route('/settings', method='GET')
def settings_view():
    SESSION = request.environ.get('beaker.session')

    settings = config.user_settings.get_all_values(SESSION.get("id", 0))
    return template("settings.tpl", settings=settings)


@app.route('/settings', method='POST')
def settings_process():
    SESSION = request.environ.get("beaker.session")

    new_forms = functions.strs_to_ints(request.forms)
    config.user_settings.multiple_set(SESSION["id"], new_forms)