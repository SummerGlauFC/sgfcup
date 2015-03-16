from db import DB
import functions
from picklesettings import PickleSettings

base = "/path/to/base/folder"  # base folder

Settings = {
    "ssl": True, # if to use https in urls or not
    "use_nginx_sendfile": False, # use nginx xsendfile instead of static_file?
    "directories": {
        "files": base + "/img/p/",  # private image location
        "thumbs": base + "/img/t/",  # thumbnail location
        "url": "sgfc.co",  # URL for this script
        "base": base,
        "template_base": "/path/to/base_folder_for_independant_templates"
    },
    "database": {
        "user": "username",  # database user
        "password": "password",  # db user password
        "db": "database_name"  # database name
    },
    "admin": {
        "username": "password" # admin login details
    }
}

Settings["directories"]["base"] = base

# /-----------------------------------------------------------------\
# |  Please try not to adjust any of the below without good reason. |
# \-----------------------------------------------------------------/

# Sortmodes used by the gallery ("Name", "database column", "sort order")
sortmodes = [
    ["Date (descending)", "id", "DESC"],
    ["Date (ascending)", "id", "ASC"],
    ["Hits (descending)", "hits", "DESC"],
    ["Hits (ascending)", "hits", "ASC"],
    ["Size", "size", "DESC"]
]

# Search modes used by the gallery ("Name", "database column")
searchmodes = [
    ["Filename", "original"],
    ["Short URL", "shorturl"]
]

# File type definitions used by the gallery
file_types = ["image", "file", "paste"]
file_type = {
    "image": 0,
    "file": 1,
    "paste": 2
}

# Initalize database connection
db = DB(user=Settings['database']['user'], password=Settings['database']
        ['password'], database=Settings['database']['db'])

# This json file contains the configuration for all user settings.
# Default settings can be changed in this file.
user_settings = PickleSettings("project/user_settings.json", db)
