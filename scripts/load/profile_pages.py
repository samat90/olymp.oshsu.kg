"""Per-page query count and time for the hot olympiad pages (run with manage.py shell, laptop copy only).

    DJANGO_SETTINGS_MODULE=dmoj.dev_wsl_settings python manage.py shell < scripts/load/profile_pages.py
"""
import time

from django.conf import settings
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext

settings.ALLOWED_HOSTS = ['*']
C = 'load1000'
PAGES = [
    '/', '/problems/', '/problem/000001', '/problem/000001/submit', '/submissions/',
    '/contests/', '/contest/%s' % C, '/contest/%s/ranking/' % C, '/contest/%s/submissions/load0001/' % C,
    '/users/', '/status/',
]
c = Client()
assert c.login(username='load0001', password='load-pass-2026')
for url in PAGES:
    for i in range(2):
        with CaptureQueriesContext(connection) as q:
            t = time.time()
            r = c.get(url, HTTP_HOST='127.0.0.1')
            dt = (time.time() - t) * 1000
    dbt = sum(float(x['time']) for x in q.captured_queries) * 1000
    print('%-45s %s %4d ms  %3d queries  db %4.0f ms' % (url, r.status_code, dt, len(q), dbt))
