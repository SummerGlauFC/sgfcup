import os

import pymysql

from migrations import db
from migrations import logger
from migrations import make_database_backup
from project.constants import FileType
from project.functions import is_image
from project.services.file import FileService

make_database_backup(os.path.basename(__file__))

# add type column
try:
    db.execute(
        "ALTER TABLE `files` ADD `type` INT UNSIGNED NOT NULL DEFAULT %s",
        [FileType.FILE.value],
    )
    logger.info("Added `type` column to `files`")
except pymysql.err.OperationalError:
    logger.warning("`type` column already exists")

# add resolution columns
try:
    db.execute("ALTER TABLE `files` ADD `width` MEDIUMINT UNSIGNED NULL")
    logger.info("Added `width` column to `files`")
except pymysql.err.OperationalError:
    logger.warning("`width` column already exists")

try:
    db.execute("ALTER TABLE `files` ADD `height` MEDIUMINT UNSIGNED NULL")
    logger.info("Added `height` column to `files`")
except pymysql.err.OperationalError:
    logger.warning("`height` column already exists")

logger.info("Processing `files`...")

for file in db.select("files"):
    data = {"type": FileType.FILE}
    if file["ext"] == "paste":
        data["type"] = FileType.PASTE
    else:
        path = FileService.get_file_path(file)
        image = is_image(path)
        if image:
            data["type"] = FileType.IMAGE
            width, height = image.size
            data["width"] = width
            data["height"] = height

    # convert the enum to its value
    data["type"] = data["type"].value

    db.update("files", data, {"id": file["id"]})
