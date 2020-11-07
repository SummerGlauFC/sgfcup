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
    ("Date (descending)", "id", "DESC"),
    ("Date (ascending)", "id", "ASC"),
    ("Hits (descending)", "hits", "DESC"),
    ("Hits (ascending)", "hits", "ASC"),
    ("Size", "size", "DESC"),
]

# Search modes used by the gallery ('Name', 'database column')
search_modes = [("Filename", "original"), ("Short URL", "shorturl")]


class FileType(Enum):
    IMAGE = 0
    FILE = 1
    PASTE = 2
    ALL = 3


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
