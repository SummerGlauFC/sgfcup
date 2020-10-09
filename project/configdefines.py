from enum import Enum

# /-----------------------------------------------------------------\
# |  Please try not to adjust any of the below without good reason. |
# \-----------------------------------------------------------------/

# Sort modes used by the gallery ('Name', 'database column', 'sort order')
sort_modes = [
    ["Date (descending)", "id", "DESC"],
    ["Date (ascending)", "id", "ASC"],
    ["Hits (descending)", "hits", "DESC"],
    ["Hits (ascending)", "hits", "ASC"],
    ["Size", "size", "DESC"],
]

# Search modes used by the gallery ('Name', 'database column')
search_modes = [["Filename", "original"], ["Short URL", "shorturl"]]

# File type definitions used by the gallery
file_types = ["image", "file", "paste"]

# Default query params for the gallery
gallery_params = {
    "sort": "0",
    "in": "0",
    "page": "1",
    "case": "0",
}


class FileType(Enum):
    IMAGE = 0
    FILE = 1
    PASTE = 2


class PasteAction(Enum):
    NONE = ""
    EDIT = "edit"
    DIFF = "diff"
    RAW = "raw"

    @staticmethod
    def get(key):
        try:
            return PasteAction(key)
        except ValueError:
            return PasteAction.NONE
