import sys
from enum import Enum

if sys.version_info >= (3, 8):
    # noinspection PyUnresolvedReferences
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    # noinspection PyUnresolvedReferences
    from typing_extensions import TypedDict

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
