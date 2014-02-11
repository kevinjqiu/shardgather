from __future__ import print_function
import re
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


DEFAULT_POOLSIZE = 5


def query(conn, sql):
    with contextlib.closing(conn.cursor()) as cursor:
        cursor.execute(sql)
        return cursor.fetchall()


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
            log.exception(e)


def collect((sql, hostname, username, password, db_name)):
    log.info(db_name)
    with contextlib.closing(mdb.connect(
        hostname, username, password,
        db=db_name, cursorclass=mdb.cursors.DictCursor)
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
    current_aggregated[db_name] = collected
    return current_aggregated


def render_plain(collected):
    return '\n'.join(
        ["Total: %d" % len(collected),
         "-" * 64,
         pprint.pformat(collected)])


def render_table(collected):
    if not collected:
        return "No output"

    from prettytable import PrettyTable
    pt = PrettyTable()

    for live in collected:
        for entry in collected[live]:
            if not pt.field_names:
                pt.field_names = ['db_name'] + list(entry.keys())
            pt.add_row([live] + entry.values())
    return str(pt)


render = render_table


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
    pool_size = int(config_parser.get(
        'executor', 'pool_size', DEFAULT_POOLSIZE))
    shard_name_pattern = config_parser.get('database', 'shard_name_pattern')

    is_shard_db = re.compile(shard_name_pattern).search

    log.info('SQL to be executed for each database:\n%s', sql)

    password = getpass.getpass()
    with contextlib.closing(
        mdb.connect(hostname, username, password)
    ) as conn:
        try:
            shard_databases = get_shard_databases(
                hostname, username, password, is_shard_db)
        except mdb.Error as e:
            log.exception(e)

    pool = Pool(pool_size)

    collected = reduce(
        aggregate,
        pool.map(collect, [(sql, hostname, username, password, live) for live in shard_databases]),
        {}
    )
    print(render(collected))


if __name__ == '__main__':
    main()
