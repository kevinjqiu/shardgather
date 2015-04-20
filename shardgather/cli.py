from __future__ import print_function
import os
import re
import optparse
import getpass
import sys
import ConfigParser
from multiprocessing import Pool, current_process
from shardgather.renderers import RENDERERS, DEFAULT_RENDERER
from shardgather.db import query, get_shard_databases, get_connection


DEFAULT_POOLSIZE = 5


def print(s, out=sys.stderr):
    out.write(s)
    out.write('\n')


def render(s):
    sys.stdout.write(s)
    sys.stdout.write('\n')


def highlight(sql):
    from pygments import highlight as pygments_highlight
    from pygments.lexers import SqlLexer
    from pygments.formatters import TerminalFormatter

    return pygments_highlight(sql, SqlLexer(), TerminalFormatter())


CONNECTIONS = {}


def collect((sql, hostname, username, password, db_name)):
    print("Running on %s" % db_name)
    current_process_name = current_process().name
    if current_process_name not in CONNECTIONS:
        print("Creating a new connection for worker %s" % current_process_name)
        CONNECTIONS[current_process_name] = get_connection(
            hostname, username, password)
    conn = CONNECTIONS[current_process_name]
    query(conn, "USE %s" % db_name)
    collected = query(conn, sql.format(db_name=db_name))
    print("%d rows returned for %s" % (len(collected), db_name))
    return db_name, collected


def aggregate(current_aggregated, next):
    db_name, collected = next
    current_aggregated[db_name] = collected
    return current_aggregated


def configure():
    parser = optparse.OptionParser()
    parser.add_option(
        '-c', '--config', dest='config_file_name',
        help='Config file', metavar='PATH_TO_CONFIG_FILE')
    parser.add_option(
        '-p', '--pwdfile', dest='pwdfile',
        help='File containing database password', metavar='PATH_TO_PWD_FILE')
    parser.add_option(
        '-i', '--interactive', action='store_true',
        help=(
            'Drop into an interactive shell instead of rendering'
            'the result.'))
    parser.add_option(
        '-g', '--mkcfg', action='store_true',
        help='Generate sample config')
    return parser.parse_args()


def get_password(options):
    if options.pwdfile:
        with open(options.pwdfile) as f:
            return f.read().rstrip()

    return getpass.getpass()


def main():
    options, args = configure()

    if options.mkcfg:
        config_file = os.path.join(
            os.path.dirname(__file__), 'config.ini.sample')
        with open(config_file) as f:
            print(f.read(), out=sys.stdout)
        sys.exit(0)

    password = None
    if options.pwdfile:
        with open(options.pwdfile) as f:
            password = f.read().rstrip()

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
    renderer = RENDERERS[config_parser.get(
        'renderer', 'renderer', DEFAULT_RENDERER)]
    shard_name_pattern = config_parser.get('database', 'shard_name_pattern')

    is_shard_db = re.compile(shard_name_pattern).search

    print("Host: %s" % hostname)
    print("Username: %s" % username)
    print("Renderer: %s" % renderer.__name__)
    print("Executor Pool Size: %s" % pool_size)
    print("Interactive mode: %s" % options.interactive)
    print("SQL to be executed for each database:\n\n%s" % highlight(sql))

    password = get_password(options)

    shard_databases = get_shard_databases(
        hostname, username, password, is_shard_db)

    if not shard_databases:
        raise RuntimeError('Cannot get shard databases given the pattern: %s'
                           % shard_name_pattern)

    pool = Pool(pool_size)

    try:
        collected = reduce(
            aggregate,
            pool.map(
                collect,
                [(sql, hostname, username, password, live)
                 for live in shard_databases]),
            {}
        )

        if options.interactive:
            print("Available variables:")
            print("  collected - the collected data")
            import IPython
            IPython.embed()

        render(renderer(collected))
    finally:
        for _, conn in CONNECTIONS.iteritems():
            conn.close()
