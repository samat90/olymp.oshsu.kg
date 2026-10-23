"""Tokens for the code runner (runner/server.py).

The runner trusts a token signed with a secret shared with the site. The token
says who runs the code, which languages are allowed and the limits.
"""
import base64
import hashlib
import hmac
import json
import time

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

TOKEN_LIFETIME = 600

# Hard caps; the runner applies its own caps too.
MAX_TIME = 5.0
MAX_MEMORY = 262144


def runner_secret():
    secret = getattr(settings, 'DMOJ_RUNNER_SECRET', None)
    if not secret:
        path = getattr(settings, 'DMOJ_RUNNER_SECRET_FILE', None)
        if path:
            try:
                with open(path, 'rb') as f:
                    secret = f.read().strip()
            except OSError:
                secret = None
    if isinstance(secret, str):
        secret = secret.encode()
    return secret or None


def runner_enabled():
    return bool(public_url() and runner_secret())


def public_url():
    return getattr(settings, 'DMOJ_RUNNER_PUBLIC_URL', None)


def _b64(data):
    return base64.urlsafe_b64encode(data).decode().rstrip('=')


def make_token(user_id, languages=None, time_limit=None, memory_limit=None, lifetime=TOKEN_LIFETIME):
    secret = runner_secret()
    if not secret:
        raise ImproperlyConfigured('DMOJ_RUNNER_SECRET or DMOJ_RUNNER_SECRET_FILE must be set')
    payload = {'u': user_id, 'exp': int(time.time()) + lifetime}
    if languages is not None:
        payload['langs'] = sorted(languages)
    if time_limit:
        payload['time'] = min(float(time_limit), MAX_TIME)
    if memory_limit:
        payload['memory'] = min(int(memory_limit), MAX_MEMORY)
    body = _b64(json.dumps(payload, separators=(',', ':')).encode())
    sig = _b64(hmac.new(secret, body.encode(), hashlib.sha256).digest())
    return body + '.' + sig, payload['exp']
