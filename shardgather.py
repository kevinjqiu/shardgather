from __future__ import print_function
import optparse
import MySQLdb as mdb
import getpass
import sys
import pprint
import contextlib
import ConfigParser
import logging
from multiprocessing import Pool
from logging.config import fileConfig


log = logging.getLogger('shardgather')


POOLSIZE = 5


def query(conn, sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()


def get_live_databases(conn):
    return [
        db_name for (db_name,) in query(conn, 'SHOW DATABASES')
        if db_name.startswith('live')
    ]


def collect((sql, hostname, username, password, db_name)):
    log.info(db_name)
    with contextlib.closing(
            mdb.connect(hostname, username, password, db=db_name)
    ) as conn:
        try:
            query(conn, "USE %s" % db_name)
            collected = query(conn, sql % dict(db_name=db_name))
            log.info("%s:\t%d", db_name, len(collected))
            return db_name, collected
        except mdb.Error as e:
            log.exception(e)


def aggregate(current_aggregated, next):
    db_name, collected = next
    current_aggregated.extend(collected)
    return current_aggregated


def configure():
    parser = optparse.OptionParser()
    parser.add_option(
        '-c', '--config', dest='config_file_name',
        help='Config file', metavar='PATH_TO_CONFIG_FILE')
    return parser.parse_args()


def main():
    options, args = configure()

    fileConfig(options.config_file_name)

    if len(args) != 1:
        raise RuntimeError('sql file needed')

    if args[0] == '-':
        sql_file = sys.stdin
    else:
        sql_file = open(args[0], 'r')

    sql = sql_file.read()
    sql_file.close()

    config_parser = ConfigParser.ConfigParser()
    config_parser.read([options.config_file_name])
    hostname = config_parser.get('database', 'hostname')
    username = config_parser.get('database', 'username')

    log.info('SQL to be executed for each database:\n%s', sql)

    password = getpass.getpass()
    with contextlib.closing(
        mdb.connect(hostname, username, password)
    ) as conn:
        try:
            live_databases = get_live_databases(conn)
        except mdb.Error as e:
            log.exception(e)

    pool = Pool(POOLSIZE)

    collected = reduce(
        aggregate,
        pool.map(collect, [(sql, hostname, username, password, live) for live in live_databases]),
        []
    )
    print("Total: %d" % len(collected))
    print("-" * 64)
    print(pprint.pformat(collected))

if __name__ == '__main__':
    main()
