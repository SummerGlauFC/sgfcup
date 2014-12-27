from project import app, functions, config
from bottle import static_file, request
from bottle import jinja2_view as view, jinja2_template as template


@app.route('/settings', method='GET')
def settings_view():
    SESSION = request.environ.get('beaker.session')

    settings = config.user_settings.get_all_values(SESSION.get("id", 0))
    return template("settings.tpl", settings=settings)