import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')

try:
    import MySQLdb  # noqa: F401, imported for side effect
except ImportError:
    try:
        import pymysql
    except ImportError:
        pymysql = None
    if pymysql is not None:
        pymysql.install_as_MySQLdb()

from django.core.wsgi import get_wsgi_application  # noqa: E402, django must be imported here
application = get_wsgi_application()
