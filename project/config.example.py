from project.configdefines import *

base = "/path/to/base/folder"  # base folder

Settings = {
    "ssl": True,  # if to use https in urls or not
    # refer to the README on how to configure the following option
    "use_nginx_sendfile": False,  # use nginx xsendfile instead of static_file?
    "directories": {
        "files": base + "/img/p/",  # private image location
        "thumbs": base + "/img/t/",  # thumbnail location
        "url": "sgfc.co",  # URL for this script
        "template_base": base
    },
    "database": {
        "user": "username",  # database user
        "password": "password",  # db user password
        "db": "database_name"  # database name
    },
    "admin": {
        "username": "password"  # admin login details
    }
}

# Initalize database connection
db = DB(user=Settings['database']['user'], password=Settings['database']
        ['password'], database=Settings['database']['db'])

# This json file contains the configuration for all user settings.
# Default settings can be changed in this file.
user_settings = PickleSettings("project/user_settings.json", db)
