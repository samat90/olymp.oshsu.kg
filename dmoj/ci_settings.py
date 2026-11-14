"""Settings for GitHub Actions (.github/workflows/ci.yml): PostgreSQL from the environment, no external services.

Run with DJANGO_SETTINGS_MODULE=dmoj.ci_settings. Never use on the server.
"""
import os

from dmoj.settings import *  # noqa: F401, F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('CI_DB_NAME', 'olymp_ci'),
        'USER': os.environ.get('CI_DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('CI_DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('CI_DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('CI_DB_PORT', '5432'),
        'OPTIONS': {'options': '-c jit=off'},
    },
}

# True at load time: the Jinja test instrumentation (response.context) depends on it; the test runner turns it off.
DEBUG = True
ALLOWED_HOSTS = ['*']
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECRET_KEY = 'ci-only-not-a-secret'

# Same as the local test settings: the upstream tests expect English and free-form problem codes.
LANGUAGE_CODE = 'en'
DMOJ_NUMERIC_PROBLEM_CODES = False

EVENT_DAEMON_USE = False
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# What the server keeps in the untracked dmoj/local_settings.py and a clean checkout lacks.
STATIC_ROOT = os.path.join(BASE_DIR, 'static')  # noqa: F405
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # noqa: F405
MEDIA_URL = '/media/'
COMPRESS_OUTPUT_DIR = 'cache'
STATICFILES_FINDERS += ('compressor.finders.CompressorFinder',)  # noqa: F405
COMPRESS_ENABLED = False
DMOJ_PROBLEM_DATA_ROOT = os.path.join(BASE_DIR, 'problems')  # noqa: F405
REGISTRATION_OPEN = True
DMOJ_REQUIRE_STAFF_2FA = False
DMOJ_2FA_HARDCORE = False
WEBAUTHN_RP_ID = None
TIME_ZONE = 'Asia/Bishkek'
DEFAULT_USER_TIME_ZONE = 'Asia/Bishkek'
SITE_NAME = 'OshSU Olymp'
SITE_LONG_NAME = 'OshSU Olymp'
SITE_ADMIN_EMAIL = 'admin@example.invalid'
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}

from django.utils.translation import gettext_lazy as _  # noqa: E402

LANGUAGES = [('ru', _('Русский')), ('en', _('English')), ('ky', _('Кыргызча'))]
