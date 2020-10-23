import hashlib
import random
from typing import Optional
from typing import Tuple

from project import db
from project.constants import TypedDict
from project.functions import id_generator


class PasteInterface(TypedDict, total=False):
    id: int
    userid: int
    shorturl: str
    name: str
    lang: str
    content: str


class RevisionInterface(TypedDict, total=False):
    id: int
    pasteid: int
    userid: int
    commit: str
    message: str
    paste: str
    fork: bool
    parent: int
    parent_revision: int


class PasteService:
    @staticmethod
    def get_by_id(paste_id: int) -> Optional[PasteInterface]:
        """
        Get a paste by its ID.

        :param paste_id: the ID of the paste
        :return: row of the paste if it exists
        """
        return db.select("pastes", where=PasteInterface(id=paste_id), singular=True)

    @staticmethod
    def get_by_url(url: str) -> Optional[PasteInterface]:
        """
        Get a paste by its URL.

        :param url: the URL of the paste
        :return: row of the paste if it exists
        """
        # BINARY used for case sensitivity
        return db.fetchone("SELECT * FROM `pastes` WHERE BINARY `shorturl` = %s", [url])

    @staticmethod
    def get_revision(attrs: RevisionInterface) -> RevisionInterface:
        """
        Get a specific paste revision.

        :param attrs: attributes to get revision by
        :return: row of the revision if it exists
        """
        return db.select("revisions", where=attrs, singular=True)

    @staticmethod
    def get_revisions(attrs: RevisionInterface) -> Tuple[RevisionInterface, ...]:
        """
        Get all matching revisions.

        :param attrs: attributes to get revisions by
        :return: Tuple of matching revisions
        """
        return db.select("revisions", where=attrs)

    @staticmethod
    def get_commit_hash(body: str):
        """
        Get the commit hash for the given paste content.

        :param body: content to get hash for
        :return: hash for given content
        """
        return hashlib.sha1(body.encode("utf-8")).hexdigest()[0:7]

    @staticmethod
    def upload(new_attrs: PasteInterface) -> PasteInterface:
        """
        Upload a given paste.

        :param new_attrs: paste to upload
        :return: the uploaded paste
        """
        # Generate random file name
        shorturl = id_generator(random.SystemRandom().randint(4, 7))

        # insert paste to pastes table first...
        paste = PasteService.create(
            PasteInterface(
                userid=new_attrs["userid"],
                shorturl=shorturl,
                name=new_attrs["name"],
                lang=new_attrs["lang"],
                content=new_attrs["content"],
            )
        )
        paste_row = paste["id"]

        # ... then add to files table
        # imported locally to avoid circular imports
        from project.services.file import FileService
        from project.services.file import FileInterface

        FileService.create(
            FileInterface(
                userid=new_attrs["userid"],
                shorturl=shorturl,
                ext="paste",
                original=paste_row,
                size=len(new_attrs["content"]),
            )
        )

        return paste

    @staticmethod
    def create(new_attrs: PasteInterface) -> PasteInterface:
        """
        Create an account with the given values.

        :param new_attrs: dict of values to use
        :return: the created account
        """
        paste = db.insert("pastes", new_attrs)
        return PasteService.get_by_id(paste.lastrowid)

    @staticmethod
    def create_revision(new_attrs: RevisionInterface) -> RevisionInterface:
        """
        Create an account with the given values.

        :param new_attrs: dict of values to use
        :return: the created account
        """
        rev = db.insert("revisions", new_attrs)
        return PasteService.get_revision(RevisionInterface(id=rev.lastrowid))

    @staticmethod
    def delete(paste_id: int):
        """
        Delete the given paste, and its revisions.

        :param paste_id: the ID of the paste to delete
        """
        db.delete("revisions", RevisionInterface(pasteid=paste_id))
        db.delete("pastes", PasteInterface(id=paste_id))

    @staticmethod
    def get_latest_revision(paste: PasteInterface) -> Optional[RevisionInterface]:
        """
        Get the latest revision for the given paste.

        :param paste: paste row (only id is needed)
        :return: latest revision of the paste, else None
        """
        return db.fetchone(
            "SELECT * FROM `revisions` WHERE `pasteid` = %s ORDER BY `id` DESC LIMIT 1",
            [paste["id"]],
        )

    @staticmethod
    def get_content(paste: PasteInterface, commit: str = None) -> Optional[str]:
        """
        Get the content of a specific paste at a specific revision.

        :param commit: commit of revision ("latest" will get the most recent commit)
        :param paste: paste row if already available
        :return: content for the given paste if it exists, else None
        """
        if commit == "latest":
            # get latest revision
            revision = PasteService.get_latest_revision(paste)
        else:
            revision = PasteService.get_revision(
                RevisionInterface(pasteid=paste["id"], commit=commit)
            )

        if revision:
            return revision["paste"]
        elif paste:
            return paste["content"]
        return None

    @staticmethod
    def get_parent(rev: RevisionInterface) -> Tuple[PasteInterface, Optional[str], str]:
        """
        Get the parent revision/paste for the given revision.

        :param rev: revision to get parent of
        :return: Tuple of (parent, parent_commit, parent_content)
        """
        parent_commit = None
        if rev["parent_revision"]:
            parent_rev = PasteService.get_revision(
                RevisionInterface(id=rev["parent_revision"])
            )
            parent_commit = parent_rev["commit"]
            parent = PasteService.get_by_id(parent_rev["pasteid"])
        else:
            parent = PasteService.get_by_id(rev["parent"])
        parent_content = PasteService.get_content(commit=parent_commit, paste=parent)
        return parent, parent_commit, parent_content
