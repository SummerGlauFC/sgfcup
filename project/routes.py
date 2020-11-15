from flask import Flask


def register_routes(app: Flask):
    from project.controllers.admin import blueprint as admin_blueprint
    from project.controllers.gallery import blueprint as gallery_blueprint
    from project.controllers.settings import blueprint as settings_blueprint
    from project.controllers.static import blueprint as static_blueprint
    from project.controllers.upload import blueprint as upload_blueprint
    from project.controllers.view import blueprint as view_blueprint

    app.register_blueprint(admin_blueprint)
    app.register_blueprint(gallery_blueprint)
    app.register_blueprint(settings_blueprint)
    app.register_blueprint(static_blueprint)
    app.register_blueprint(upload_blueprint)
    app.register_blueprint(view_blueprint)

    # only register the oauth routes if enabled
    if app.config["AUTH_OPENID_ENABLED"]:
        from project.controllers.oauth import blueprint as oauth_blueprint

        app.register_blueprint(oauth_blueprint)
