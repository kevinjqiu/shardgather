import MySQLdb as mdb
import getpass
import sys
import pprint
import contextlib

HOSTNAME = 'orddb02'
USERNAME = 'kevinqiu'
POOLSIZE = 5


def log(text):
    print >> sys.stdout, text


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
    log(db_name)
    with contextlib.closing(
            mdb.connect(HOSTNAME, USERNAME, password, db=db_name)
    ) as conn:
        try:
            query(conn, "USE %s" % db_name)
            collected = query(conn, sql % dict(db_name=db_name))
            log('%s:\t%d' % (db_name, len(collected)))
            return db_name, collected
        except mdb.Error as e:
            log(str(e))


def aggregate(current_aggregated, next):
    db_name, collected = next
    current_aggregated.extend(collected)
    return current_aggregated


def main():
    if len(sys.argv) != 2:
        raise RuntimeError('sql file needed')

    sql_file = sys.argv[1]

    with open(sql_file) as f:
        sql = f.read()

    log('SQL to be executed for each database:')
    log(sql)

    password = getpass.getpass()
    with contextlib.closing(
        mdb.connect(HOSTNAME, USERNAME, password)
    ) as conn:
        try:
            live_databases = get_live_databases(conn)
        except mdb.Error as e:
            log(str(e))

    from multiprocessing import Pool
    pool = Pool(POOLSIZE)

    collected = reduce(
        aggregate,
        pool.map(collect, [(sql, HOSTNAME, USERNAME, password, live) for live in live_databases]),
        []
    )
    log("Total: %d" % len(collected))
    log("-" * 64)
    log(pprint.pformat(collected))

if __name__ == '__main__':
    main()
