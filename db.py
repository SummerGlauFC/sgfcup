from __future__ import division, print_function, absolute_import
import cymysql
import inspect


class BaseDB(object):
    ''' a small database abstraction to eliminate lost connections '''

    conn = None
    ''' the cymysql connection instance '''

    cur = None
    ''' the cymysql cursor instance '''

    retries = 3
    ''' number of retries for a failed operation '''

    def __init__(self, host='localhost', user='root', password='', database=''):
        ''' initialize the object '''
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self._init_connection()

    def _init_connection(self):
        ''' initializes the connection '''

        if self.retries < 1:
            raise DBConnectionFailed()
        try:
            self.conn = cymysql.connect(host=self.host, user=self.user,
                                        passwd=self.password, db=self.database,
                                        connect_timeout=604800, charset='utf8',
                                        use_unicode=True)
            self.cur = self.conn.cursor(cymysql.cursors.DictCursor)
        except:
            self.retries -= 1
            print("WARNING: MySQL connection died, trying to reinit...")
            self._init_connection()

    def escape(self, obj):
        ''' autodetect input and escape it for use in a SQL statement '''

        try:
            if isinstance(obj, str):
                return self.conn.escape(obj)
            else:
                return obj
        except cymysql.OperationalError:
            print("WARNING: MySQL connection died, trying to reinit...")
            self._init_connection()
            return self.escape(obj)

    def execute(self, sql, args=None):
        ''' execute the SQL statement and return the cursor '''
        try:
            self.cur.execute(
                sql, args) if args is not None else self.cur.execute(sql)
            return self.cur
        except cymysql.OperationalError:
            print("WARNING: MySQL connection died, trying to reinit...")
            self._init_connection()
            return self.execute(sql, args)

    def fetchone(self, sql, args=None):
        ''' execute the SQL statement and return one row if there's a result, return None if there's no result '''

        cur = self.execute(sql, args)
        if cur.rowcount:
            return cur.fetchone()
        else:
            return None

    def fetchall(self, sql, args=None):
        ''' execute the SQL statement and return one row if there's a result, return None if there's no result '''

        cur = self.execute(sql, args)
        if cur.rowcount:
            return cur.fetchall()
        else:
            return None


class DB(BaseDB):
    ''' Wrapper around small DB abstraction to abstract further
        this is art.
    '''

    def __init__(self, *args, **kwargs):
        self.debug = kwargs.pop('debug', False)
        super(DB, self).__init__(*args, **kwargs)

    @staticmethod
    def _debug_print(*args):
        print(args)
        (frame, filename, line_number, function_name, lines,
         index) = inspect.getouterframes(inspect.currentframe())[2]
        formatted = "\t{filename}:{line_number} in {function_name}\n\t-->\t{lines}".format(
            filename=filename, line_number=line_number, function_name=function_name, lines='\n'.join([x.strip() for x in lines]))
        print(formatted)
        print("-" * 40)

    def _pairs_generator(self, pairs, joiner=' AND ', brackets=False):
        ''' builds a where template '''
        base = '`{0}` = %s'
        if brackets:
            base = '({})'.format(base)
        return joiner.join([base.format(key) for key in pairs])

    def _columns_generator(self, columns):
        return self._pairs_generator(columns, joiner=', ')

    def select(self, table, what="*", where=None, singular=False):
        ''' build and execute a select operation, usage:
                select('rooms', what='*', where={"name": "#main"})
            resulting in the query:
                'SELECT * FROM `rooms` WHERE `name` = %s', ['#main']
        '''
        if type(what) is not list or type(what) is not tuple:
            what = [what]
        else:
            _what = []
            for item in what:
                if item is not "*":
                    _what.append("`{}`".format(item))
                else:
                    _what.append("*")
            what = _what

        query = 'SELECT {what} FROM `{table}`'
        if where:
            query += ' WHERE {where}'
        else:
            where = {}

        query = query.format(
            what=", ".join(what), table=table, where=self._pairs_generator(where, brackets=True))

        if self.debug:
            self._debug_print(query, list(where.values()))

        if singular:
            return self.fetchone(query, list(where.values()))
        else:
            return self.fetchall(query, list(where.values()))

    def update(self, table, set_pairs, where_pairs):
        ''' build and execute an update operation, usage:
                update('table', {"hidden": True, "other": "test"}, {"name": "#main", "me": "test again"})
            resulting in the query:
                'UPDATE `rooms` SET `hidden` = %s, `other` = %s WHERE `me` = %s AND `name` = %s', [True, 'test', 'test again', '#main'])
        '''
        query = 'UPDATE `{table}` SET {sets} WHERE {where}'.format(
            table=table, sets=self._columns_generator(set_pairs), where=self._pairs_generator(where_pairs, brackets=True))

        if self.debug:
            self._debug_print(query, list(set_pairs.values()) + list(where_pairs.values()))

        return self.execute(query, list(set_pairs.values()) + list(where_pairs.values()))

    def delete(self, table, pairs):
        ''' build and execute a delete operation, usage:
                delete('table', {'c1': 'v1', 'c2': 'v2'})
            resulting in the query:
                'DELETE FROM `table` WHERE `c1` = %s AND `c2` = %s', ['v1', 'v2']
        '''

        where = self._pairs_generator(pairs, brackets=True)
        query = 'DELETE FROM `{table}` WHERE {where}'.format(
            table=table, where=where)

        if self.debug:
            self._debug_print(query, list(pairs.values()))

        return self.execute(query, list(pairs.values()))

    def insert(self, table, columns_pair):
        ''' build and execute an insert operation, as such:
            insert('table_name', {'column1': 'value', 'column2': 'value2'}) '''

        columns = ', '.join(['`{}`'.format(_) for _ in columns_pair])
        values = ', '.join(['%s' for _ in columns_pair])

        query = 'INSERT INTO `{table}` ({columns}) VALUES ({values})'.format(
            table=table, columns=columns, values=values)

        if self.debug:
            self._debug_print(query, list(columns_pair.values()))

        return self.execute(query, list(columns_pair.values()))


class DBConnectionFailed(Exception):

    ''' happens when a database operation continually fails '''
