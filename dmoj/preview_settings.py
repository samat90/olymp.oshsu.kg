"""Explicit local UI/test settings: never use this module for production."""
import os

from dmoj.settings import *  # noqa: F403

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3',
                         'NAME': os.path.join(BASE_DIR, 'ui-preview.sqlite3')}}
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'testserver']
DEBUG = True
COMPRESS_ENABLED = False
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
