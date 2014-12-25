import cymysql


class DB(object):

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
            print "WARNING: MySQL connection died, trying to reinit..."
            self._init_connection()

    def escape(self, obj):
        ''' autodetect input and escape it for use in a SQL statement '''

        try:
            if isinstance(obj, str):
                return self.conn.escape(obj)
            else:
                return obj
        except cymysql.OperationalError:
            print "WARNING: MySQL connection died, trying to reinit..."
            self._init_connection()
            return self.escape(obj)

    def execute(self, sql, args=None):
        ''' execute the SQL statement and return the cursor '''
        print sql, args
        try:
            self.cur.execute(
                sql, args) if args is not None else self.cur.execute(sql)
            return self.cur
        except cymysql.OperationalError:
            print "WARNING: MySQL connection died, trying to reinit..."
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

    def insert(self, table, columns_pair):
        ''' build and execute an insert operation, as such:
            insert('table_name', {'column1': 'value', 'column2': 'value2'}) '''

        columns = ', '.join(['`{0}`'.format(key) for key in columns_pair])
        values = ', '.join(['%s' for _ in range(len(columns_pair))])

        query = 'INSERT INTO `{table}` ({columns}) VALUES ({values})'.format(
            table=table, columns=columns, values=values)

        return self.execute(query, [value for value in columns_pair.values()])


class DBConnectionFailed(Exception):

    ''' happens when a database operation continually fails '''
