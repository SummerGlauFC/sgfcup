import logging
from functools import wraps

import pymysql
from flask.logging import default_handler

logger = logging.getLogger(__name__)
logger.addHandler(default_handler)


def catch_error(f):
    @wraps(f)
    def wrapped(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except (pymysql.err.Error, BrokenPipeError):
            logger.exception("Database connection died, trying to reinitialise...")
            self._init_connection()
            return f(self, *args, **kwargs)

    return wrapped


class DBConnectionFailed(Exception):
    """ happens when a database operation continually fails """


class BaseDB(object):
    """ a database abstraction to eliminate lost connections """

    # the connection instance
    _conn = None

    # the cursor instance
    cur = None

    # number of retries for a failed operation
    retries = 3

    def __init__(self, host="localhost", user="root", password="", database=""):
        """ initialize the object """
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def _init_connection(self):
        """ initializes the connection """
        if self.retries < 1:
            logger.exception("Database connection died, maximum retries succeeded")
            raise DBConnectionFailed()

        try:
            return self._connect()
        except (pymysql.err.Error, BrokenPipeError):
            logger.exception("Database connection died, trying to reinitialise...")
            self.retries -= 1
            return self._init_connection()

    def _connect(self):
        """ connect to the database """
        conn = pymysql.connect(
            host=self.host,
            user=self.user,
            passwd=self.password,
            db=self.database,
            connect_timeout=604800,
            charset="utf8",
            use_unicode=True,
        )
        # autocommit just in case we're on InnoDB
        conn.autocommit(True)
        return conn

    @property
    def conn(self):
        if self._conn is None:
            self._conn = self._init_connection()
        return self._conn

    def close(self):
        """ close the database connection """
        self.conn.close()
        self._conn = None

    def escape(self, obj):
        """ autodetect input and escape it for use in a SQL statement """
        if isinstance(obj, str):
            return self.conn.escape(obj)
        return obj

    def execute(self, sql, args=None):
        """ execute the SQL statement and return the cursor """
        logger.debug(f'"{sql}" {args}')
        conn = self.conn
        self.cur = conn.cursor(pymysql.cursors.DictCursor)
        self.cur.execute(sql, args) if args is not None else self.cur.execute(sql)
        return self.cur

    def fetchone(self, sql, args=None):
        """ execute the SQL statement and return one row if there's a result, return None if there's no result """
        cur = self.execute(sql, args)
        if cur.rowcount:
            return cur.fetchone()
        return None

    def fetchall(self, sql, args=None):
        """ execute the SQL statement and return one row if there's a result, return None if there's no result """
        cur = self.execute(sql, args)
        if cur.rowcount:
            return cur.fetchall()
        return None


class DB(BaseDB):
    """
    Wrapper around small DB abstraction to abstract further.

    this is art.
    """

    def __init__(self, pool=None, *args, **kwargs):
        self.debug = kwargs.pop("debug", False)
        if self.debug:
            logger.setLevel(logging.DEBUG)
        self.pool = pool
        super(DB, self).__init__(*args, **kwargs)

    @property
    def conn(self):
        if self._conn is None:
            self._conn = self.pool.dedicated_connection()
        return self._conn

    def _pairs_generator(self, pairs, joiner=" AND ", brackets=False):
        """ builds a where template """
        base = "`{0}` = %s"
        if brackets:
            base = f"({base})"
        return joiner.join([base.format(key) for key in pairs])

    def _columns_generator(self, columns):
        return self._pairs_generator(columns, joiner=", ")

    def select(self, table, what="*", where=None, singular=False):
        """build and execute a select operation, usage:
            select('rooms', what='*', where={'name': '#main'})
        resulting in the query:
            'SELECT * FROM `rooms` WHERE `name` = %s', ['#main']
        """
        if not isinstance(what, (list, tuple)):
            what = [what]
        else:
            _what = []
            for item in what:
                if item == "*":
                    _what.append(f"`{item}`")
                else:
                    _what.append("*")
            what = _what

        query = "SELECT {what} FROM `{table}`"
        if where:
            query += " WHERE {where}"
        else:
            where = {}

        query = query.format(
            what=", ".join(what),
            table=table,
            where=self._pairs_generator(where, brackets=True),
        )

        if singular:
            return self.fetchone(query, list(where.values()))
        return self.fetchall(query, list(where.values()))

    def update(self, table, set_pairs, where_pairs):
        """build and execute an update operation, usage:
            update('table', {'hidden': True, 'other': 'test'}, {'name': '#main', 'me': 'test again'})
        resulting in the query:
            'UPDATE `rooms` SET `hidden` = %s, `other` = %s WHERE `me` = %s AND `name` = %s', [True, 'test', 'test again', '#main'])
        """
        sets = self._columns_generator(set_pairs)
        where = self._pairs_generator(where_pairs, brackets=True)
        query = f"UPDATE `{table}` SET {sets} WHERE {where}"
        return self.execute(
            query, list(set_pairs.values()) + list(where_pairs.values())
        )

    def delete(self, table, pairs):
        """build and execute a delete operation, usage:
            delete('table', {'c1': 'v1', 'c2': 'v2'})
        resulting in the query:
            'DELETE FROM `table` WHERE `c1` = %s AND `c2` = %s', ['v1', 'v2']
        """

        where = self._pairs_generator(pairs, brackets=True)
        query = f"DELETE FROM `{table}` WHERE {where}"
        return self.execute(query, list(pairs.values()))

    def insert(self, table, columns_pair):
        """build and execute an insert operation, as such:
        insert('table_name', {'column1': 'value', 'column2': 'value2'})"""

        columns = ",".join([f"`{col}`" for col in columns_pair])
        values = ",".join(["%s"] * len(columns_pair))
        query = f"INSERT INTO `{table}` ({columns}) VALUES ({values})"
        return self.execute(query, list(columns_pair.values()))
