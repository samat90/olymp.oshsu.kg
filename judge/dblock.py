from itertools import chain

from django.db import connection, transaction


class LockModel(object):
    """Table lock for a block of writes.

    MySQL needs LOCK TABLES. On PostgreSQL we take an EXCLUSIVE lock inside
    a transaction instead: it blocks concurrent writers but not readers,
    which matches what the MySQL code was used for.
    """

    def __init__(self, write, read=()):
        self.write = list(write)
        self.read = list(read)
        self.mysql = connection.vendor == 'mysql'
        self.atomic = None

    def __enter__(self):
        if self.mysql:
            self.tables = ', '.join(chain(
                ('`%s` WRITE' % model._meta.db_table for model in self.write),
                ('`%s` READ' % model._meta.db_table for model in self.read),
            ))
            self.cursor = connection.cursor()
            self.cursor.execute('LOCK TABLES ' + self.tables)
            return

        self.atomic = transaction.atomic()
        self.atomic.__enter__()
        if connection.vendor == 'postgresql' and self.write:
            with connection.cursor() as cursor:
                cursor.execute('LOCK TABLE %s IN EXCLUSIVE MODE' % ', '.join(
                    connection.ops.quote_name(model._meta.db_table) for model in self.write))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.mysql:
            return self.atomic.__exit__(exc_type, exc_val, exc_tb)

        if exc_type is None:
            transaction.commit()
        else:
            transaction.rollback()
        self.cursor.execute('UNLOCK TABLES')
        self.cursor.close()
