"""Production-like settings for load tests in WSL (DEBUG off, Redis cache)."""
from dmoj.dev_wsl_settings import *  # noqa: F401, F403

DEBUG = False
CACHES = {
    'default': {
        'BACKEND': 'judge.utils.redis_cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    },
}
DATABASES['default']['CONN_MAX_AGE'] = 60  # noqa: F405
LOGGING = {'version': 1, 'disable_existing_loggers': False}
