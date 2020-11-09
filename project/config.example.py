base = "/path/to/base/folder"  # base folder

Settings = {
    "ssl": True,  # if to use https in urls or not
    # refer to the README on how to configure the following option
    "use_nginx_sendfile": False,  # use nginx xsendfile instead of static_file?
    "max_file_size": 1024 * 1024 * 100,  # upload size limit in bytes, default = 100MB
    "directories": {
        "files": f"{base}/img/p/",  # private image location
        "thumbs": f"{base}/img/t/",  # thumbnail location
        "url": "sgfc.co",  # URL for this script
        "template_base": base,
    },
    "database": {
        "host": "127.0.0.1",  # database host
        "user": "username",  # database user
        "password": "password",  # db user password
        "db": "database_name",  # database name
    },
    "admin": {"username": "password"},  # admin login details
    "sessions": {  # cookie encryption keys
        "validate_key": "validation-key-goes-here",
        "encrypt_key": "encryption-key-goes-here",
    },
    "debug": {  # safe to ignore, only for development
        "enabled": False,  # enable debug mode
        "sentry": {  # enable sentry bug tracking
            "enabled": False,
            "url": "https://sentry-url:goes-here@app.gensentry.com/00000",
        },
    },
}
