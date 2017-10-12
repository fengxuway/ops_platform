import pymysql as MySQLdb
from django.conf import settings
from contextlib import contextmanager
import traceback
import logging


log = logging.getLogger('django')


class DBSource(object):
    def __init__(self, host, port, user, passwd, dbname, charset='utf-8'):
        if not host:
            host = '127.0.0.1'
        if not port:
            port = 3306
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.dbname = dbname
        self.charset = charset


def default_dbsource():
    database = settings.DATABASES['default']
    host = database.get("HOST", "127.0.0.1")
    if not host:
        host = "127.0.0.1"
    port = database.get("PORT", 3306)
    if not port:
        port = 3306
    user = database.get("USER", "root")
    passwd = database.get("PASSWORD")
    db = database.get("NAME")
    charset = "utf8"
    return DBSource(host, port, user, passwd, db, charset)


@contextmanager
def connect(dbsource=None):
    """Mysql Connect Util, use 'with' to execute sqls"""
    conn = None
    try:
        if not dbsource:
            dbsource = default_dbsource()
        conn = MySQLdb.connect(
            host=dbsource.host,
            user=dbsource.user,
            port=dbsource.port,
            passwd=dbsource.passwd,
            db=dbsource.dbname,
            charset=dbsource.charset)
    except Exception as e:
        raise Exception("Database Connect Failed! Please check settings.py [DATABASES]")
    cursor = conn.cursor()
    ex = None
    try:
        yield cursor
        cursor.close()
        conn.commit()
    except Exception as e:
        ex = e
        log.error(traceback.format_exc())
        try:
            cursor.close()
        except Exception as e:
            pass
        try:
            conn.rollback()
        except Exception as e:
            pass
        traceback.print_exc()
    finally:
        try:
            conn.close()
        except Exception as e:
            pass
        if ex:
            raise ex
