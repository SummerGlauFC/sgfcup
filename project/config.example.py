from db import DB
from project.picklesettings import PickleSettings

base = "/path/to/base/folder"  # base folder

Settings = {
    "ssl": True,  # if to use https in urls or not
    # refer to the README on how to configure the following option
    "use_nginx_sendfile": False,  # use nginx xsendfile instead of static_file?
    "directories": {
        "files": f"{base}/img/p/",  # private image location
        "thumbs": f"{base}/img/t/",  # thumbnail location
        "url": "sgfc.co",  # URL for this script
        "template_base": base,
    },
    "database": {
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

# Initialize database connection
db = DB(
    user=Settings["database"]["user"],
    password=Settings["database"]["password"],
    database=Settings["database"]["db"],
    debug=Settings["debug"]["enabled"],
)

# This json file contains the configuration for all user settings.
# Default settings can be changed in this file.
user_settings = PickleSettings("project/user_settings.json", db)
