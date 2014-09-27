import contextlib
import pymysql
pymysql.install_as_MySQLdb()

import MySQLdb as mdb
from MySQLdb import cursors


def get_connection(
        hostname, username, password, cursorclass=cursors.DictCursor):
    return mdb.connect(hostname, username, password, cursorclass=cursorclass)


def query(conn, sql):
    try:
        with contextlib.closing(conn.cursor()) as cursor:
            cursor.execute(sql)
            return cursor.fetchall()
    except mdb.Error as e:
        print(str(e))


def get_shard_databases(hostname, username, password, is_shard_db):
    with contextlib.closing(
        mdb.connect(hostname, username, password)
    ) as conn:
        try:
            return [
                db_name for (db_name,) in query(conn, 'SHOW DATABASES')
                if is_shard_db(db_name)
            ]
        except mdb.Error as e:
            print(str(e))
