import os
import random
from datetime import datetime
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from PIL import Image
from PIL import ImageOps
from flask import Response
from flask import abort
from werkzeug.utils import secure_filename

from project import db
from project.extensions import user_settings
from project.constants import FileType
from project.constants import TypedDict
from project.functions import get_setting
from project.functions import id_generator
from project.functions import is_image
from project.functions import remove_transparency
from project.functions import static_file


class FileInterface(TypedDict, total=False):
    id: int
    userid: int
    shorturl: str
    ext: str
    original: Union[str, int]
    hits: int
    size: int
    date: datetime
    type: Union[int, FileType]
    width: Optional[int]
    height: Optional[int]


class FileService:
    @staticmethod
    def get_by_id(file_id: int) -> Optional[FileInterface]:
        """
        Get a file by its ID.

        :param file_id: the ID of the file
        :return: row of the file if it exists
        """
        return db.select("files", where=FileInterface(id=file_id), singular=True)

    @staticmethod
    def get_by_url(url: str) -> Optional[FileInterface]:
        """
        Get a file by its URL.

        :param url: the URL of the file
        :return: row of the file if it exists
        """
        # BINARY used for case sensitivity
        return db.fetchone("SELECT * FROM `files` WHERE BINARY `shorturl` = %s", [url])

    @staticmethod
    def upload(file, new_attrs: FileInterface) -> FileInterface:
        """
        Upload a given file.

        :param file: file to upload
        :param new_attrs: file details
        :return: the uploaded file
        """
        # Generate random file name
        shorturl = id_generator(random.SystemRandom().randint(4, 7))

        directory = get_setting("directories.files")
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        if not ext:
            ext = ""

        path = os.path.join(directory, shorturl + ext)
        file.save(path)

        data = {"type": FileType.FILE.value}
        image = is_image(path)
        if image:
            data["type"] = FileType.IMAGE.value
            width, height = image.size
            data["width"] = width
            data["height"] = height

        return FileService.create(
            FileInterface(
                userid=new_attrs["userid"],
                shorturl=shorturl,
                ext=ext,
                original=filename,
                size=os.path.getsize(path),
                **data,
            )
        )

    @staticmethod
    def create(new_attrs: FileInterface) -> FileInterface:
        """
        Create an account with the given values.

        :param new_attrs: dict of values to use
        :return: the created account
        """
        file = db.insert("files", new_attrs)
        return FileService.get_by_id(file.lastrowid)

    @staticmethod
    def delete(file: FileInterface) -> Tuple[int, str]:
        """
        Delete a file.

        :param file: file to delete
        :return: Tuple of (size, output)
        """
        size = file["size"]
        shorturl = file["shorturl"]
        original = file["original"]

        db.delete("files", FileInterface(id=file["id"]))

        # Special treatment for pastes as they don't physically exist
        # on the disk
        if file["ext"] == "paste":
            from project.services.paste import PasteService

            PasteService.delete(original)
            output = f"Removed paste {shorturl}"
        else:
            try:
                os.remove(FileService.get_file_path(file))
                output = f'Removed file "{original}" ({shorturl})'
            except OSError:
                output = f"Could not delete {shorturl}"
            try:
                thumb_dir, thumb_file = FileService.get_thumbnail_path(file)
                os.remove(os.path.join(thumb_dir, thumb_file))
            except OSError:
                # doesn't matter if we could not delete the thumbnail
                pass

        return size, output

    @staticmethod
    def delete_batch(
        files: Optional[List[FileInterface]], output: Optional[List[str]] = None
    ) -> Tuple[int, int, List[str]]:
        """
        Delete files in batch.

        :param files: list of file rows to delete
        :param output: list to output status to
        :return: Tuple of (size, count, output)
        """
        size = 0
        count = 0

        if output is None:
            output = []

        if files:
            for row in files:
                file_size, file_output = FileService.delete(row)
                count += 1
                size += file_size
                output.append(file_output)

        return size, count, output

    @staticmethod
    def increment_hits(file_id: int):
        """
        Add a hit to the given file.

        :param file_id: the ID of the file to update
        """
        db.execute("UPDATE `files` SET `hits` = `hits` + 1 WHERE `id` = %s", [file_id])

    @staticmethod
    def abort_if_invalid_url(file, filename, ext):
        """
        Abort the request if the URL does not match required form.

        :param file: file to check URL for
        :param filename: filename for URL check
        :param ext: file extension for URL check
        """
        use_extensions = user_settings.get(file["userid"], "ext")
        should_abort = False
        if filename:
            # Check for extensionless files first (e.g. Dockerfile)
            if not ext and filename != file["original"]:
                should_abort = True
            if ext and f"{filename}.{ext}" != file["original"]:
                should_abort = True
        else:
            # don't resolve if longer filename setting set, and the filename is not included.
            if use_extensions == 2:
                should_abort = True
            if ext and f".{ext}" != file["ext"]:
                should_abort = True
        if should_abort:
            abort(404)

    @staticmethod
    def serve_file(file: FileInterface) -> Response:
        """
        Serve the given file.

        :param file: file to serve.
        :return: response for the file
        """
        return static_file(
            FileService.get_file_name(file),
            root=get_setting("directories.files"),
            filename=file["original"],
        )

    @staticmethod
    def get_file_name(file: FileInterface) -> str:
        """
        Get the stored file name for the given file.

        :param file: file to get file name for
        :return: file name for file
        """
        return file["shorturl"] + file["ext"]

    @staticmethod
    def get_file_path(file: FileInterface) -> str:
        """
        Get the full path for the given file.

        :param file: file to get path for
        :return: path of file
        """
        return os.path.join(
            get_setting("directories.files"), FileService.get_file_name(file)
        )

    @staticmethod
    def get_thumbnail_path(file: FileInterface) -> Tuple[str, str]:
        """
        Get the thumbnail path for the given file.

        :param file: file to get thumbnail path for
        :return: Tuple of (thumbnail_dir, thumbnail_filename)
        """
        thumb_dir = get_setting("directories.thumbs")
        thumb_file = f"thumb_{file['shorturl']}.jpg"
        return thumb_dir, thumb_file

    @staticmethod
    def get_thumbnail(file: FileInterface) -> Optional[Response]:
        """
        Get the thumbnail for the given file.

        :param file: file to get thumbnail for
        :return: thumbnail as a response, else None
        """
        thumb_dir, thumb_file = FileService.get_thumbnail_path(file)
        if os.path.exists(os.path.join(thumb_dir, thumb_file)):
            return static_file(thumb_file, root=thumb_dir)
        return None

    @staticmethod
    def create_thumbnail(file: FileInterface, size=(400, 400)) -> Optional[Response]:
        """
        Create thumbnail for the given file.

        :param file: file to create the thumbnail for
        :param size: tuple of (width, height) for the thumbnail
        :return: thumbnail as a response or None
        """
        thumb_dir, thumb_file = FileService.get_thumbnail_path(file)
        base = Image.open(
            os.path.join(
                get_setting("directories.files"), file["shorturl"] + file["ext"]
            )
        )
        if size < base.size:
            image_info = base.info

            # rotate according to EXIF orientation
            # strip all other exif except for the orientation details
            # work around for https://github.com/python-pillow/Pillow/issues/4346
            TAG_ORIENTATION = 0x112
            exif = base.getexif()
            if len(exif):
                clean_exif = Image.Exif()
                if TAG_ORIENTATION in exif:
                    clean_exif[TAG_ORIENTATION] = exif[TAG_ORIENTATION]
                base.info["exif"] = clean_exif.tobytes()

            base = ImageOps.exif_transpose(base)
            base = ImageOps.fit(base, size, Image.ANTIALIAS)
            base = remove_transparency(base)
            base.save(os.path.join(thumb_dir, thumb_file), **image_info)
            return static_file(thumb_file, root=thumb_dir)
        return None

    @staticmethod
    def get_or_create_thumbnail(
        file: FileInterface, size=(400, 400)
    ) -> Optional[Response]:
        """
        Get (and create) the thumbnail for the given file.

        :param file: file to get/create the thumbnail for
        :param size: tuple of (width, height) for the thumbnail
        :return: thumbnail as a response or None
        """
        thumb = FileService.get_thumbnail(file)
        if not thumb:
            try:
                thumb = FileService.create_thumbnail(file, size)
            except IOError:
                return None
        return thumb
