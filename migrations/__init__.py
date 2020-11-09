import logging
import os
import subprocess
from datetime import datetime

from db import DB
from project.functions import create_pool

pool = create_pool()
db = DB(pool=pool, debug=True)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(name)-10s %(levelname)-8s %(message)s"
)
logger = logging.getLogger("migration")


def make_database_backup(migration_name="migration"):
    filename = os.path.abspath(
        datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + f"_{migration_name}_backup.sql"
    )
    with open(filename, "wb") as file:
        proc = subprocess.Popen(
            [
                "mysqldump",
                f"--user={db.user}",
                f"--password={db.password}",
                db.database,
            ],
            stdout=file,
        )
        proc.communicate()
        file.close()

    logger.info(f'Database backup saved to "{filename}"')
