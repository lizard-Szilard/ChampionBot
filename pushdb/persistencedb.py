import sys
import os
import logging
import psycopg2
from psycopg2 import extras

logger = logging.getLogger()

class PSQLdbconn:
    """Psycpog2 easy connect and quit"""

    def __init__(self, config):
        self._conn = psycopg2.connect(config)
        self._cursor = self._conn.cursor(cursor_factory=extras.DictCursor)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()

    def query(self, query, *params):
        return self._cursor.execute(query, *params)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def commit(self):
        return self._conn.commit()

    def close(self):
        self._cursor.close()
        return self._conn.close()
