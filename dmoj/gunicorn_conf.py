"""gunicorn settings for olymp.oshsu.kg.

    gunicorn -c dmoj/gunicorn_conf.py -b 127.0.0.1:8000 dmoj.wsgi:application

The site is CPU-bound (a page costs ~35 ms of CPU), so one worker per core plus one.
"""
import multiprocessing
import os

workers = int(os.environ.get('OLYMP_WEB_WORKERS', multiprocessing.cpu_count() + 1))
timeout = 60
graceful_timeout = 30
# A queue of waiting connections during the login rush at the start of an olympiad.
backlog = 2048
# Restart workers now and then so memory does not creep up during a long day.
max_requests = 3000
max_requests_jitter = 300
accesslog = os.environ.get('OLYMP_ACCESS_LOG', '/var/log/olymp/gunicorn-access.log')
errorlog = os.environ.get('OLYMP_ERROR_LOG', '/var/log/olymp/gunicorn-error.log')
