from db import DB
import functions
from picklesettings import PickleSettings

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