from db import DB
from project.picklesettings import PickleSettings
from enum import Enum

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
class file_type(Enum):
    IMAGE = 0
    FILE = 1
    PASTE = 2

PUUSH_ERROR = "-1"
