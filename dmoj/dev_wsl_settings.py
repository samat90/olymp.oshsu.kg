"""Settings for the local copy of the site running inside WSL on the laptop.

Run with DJANGO_SETTINGS_MODULE=dmoj.dev_wsl_settings. Never use on the server.
"""
from dmoj.settings import *  # noqa: F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'olymp_oshsu',
        'USER': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    },
}

DEBUG = True
ALLOWED_HOSTS = ['*']
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

DMOJ_PROBLEM_DATA_ROOT = '/opt/olymp/problems'

BRIDGED_JUDGE_ADDRESS = [('127.0.0.1', 9999)]
BRIDGED_DJANGO_ADDRESS = [('127.0.0.1', 9998)]

EVENT_DAEMON_USE = False

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Code runner on the local judge (see runner/).
DMOJ_RUNNER_PUBLIC_URL = 'http://127.0.0.1:9910'
DMOJ_RUNNER_SECRET_FILE = '/opt/judge/runner.secret'
