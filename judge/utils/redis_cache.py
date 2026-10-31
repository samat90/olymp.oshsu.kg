"""Django's Redis cache, keeping one client per process instead of building one for every operation.

Django creates a new redis.Redis object (cheap pool, costly object) on each cache call; on hot polling
endpoints that was about a quarter of the request time. Use in CACHES:

    'BACKEND': 'judge.utils.redis_cache.RedisCache'
"""
from django.core.cache.backends.redis import RedisCache as DjangoRedisCache, RedisCacheClient as DjangoClient


class RedisCacheClient(DjangoClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._clients = {}

    def get_client(self, key=None, *, write=False):
        index = self._get_connection_pool_index(write)
        client = self._clients.get(index)
        if client is None:
            client = self._clients[index] = self._client(connection_pool=self._get_connection_pool(write))
        return client


class RedisCache(DjangoRedisCache):
    def __init__(self, server, params):
        super().__init__(server, params)
        self._class = RedisCacheClient
