"""Attendance counters for the admins' dashboard.

Everything lives in Redis and is only aggregated: unique visitors are HyperLogLog sketches (no list of who came),
pages and referring sites are counters. The database is never touched and nothing personal is stored.
Writes happen from judge.utils.online.record(), at most once per THROTTLE seconds per visitor and page.
Keys expire by themselves; days and hours are in the site's local time zone.
"""
import re
import time
from datetime import datetime, timedelta
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.cache import cache

PREFIX = 'olst:'
DAY = 86400
KEEP_DAYS = 100 * DAY       # daily visitors and views
KEEP_DETAIL = 36 * DAY      # hours, pages, sources, devices
KEEP_SLOTS = 3 * DAY        # 5-minute buckets for the peak
SLOT_MINUTES = 5
HISTORY_DAYS = 30
HEAT_DAYS = 28
TOP = 10
MAX_TRACKED = 300           # pages and referring sites kept per day

DEVICES = ('desktop', 'mobile', 'tablet')
BROWSERS = (
    ('Yandex', ('YaBrowser',)),
    ('Edge', ('Edg/', 'EdgA/', 'EdgiOS/')),
    ('Opera', ('OPR/', 'Opera')),
    ('Samsung', ('SamsungBrowser',)),
    ('Firefox', ('Firefox/', 'FxiOS/')),
    ('Chrome', ('Chrome/', 'CriOS/')),
    ('Safari', ('Safari/',)),
)
BROWSER_NAMES = tuple(name for name, _ in BROWSERS) + ('other',)

HOST_RE = re.compile(r'^[a-z0-9-]+(\.[a-z0-9-]+)+$')
LOCAL_HOST_RE = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')


def device_of(ua):
    if 'iPad' in ua or 'Tablet' in ua or ('Android' in ua and 'Mobi' not in ua):
        return 'tablet'
    if 'Mobi' in ua or 'iPhone' in ua or 'Android' in ua:
        return 'mobile'
    return 'desktop'


def browser_of(ua):
    for name, markers in BROWSERS:
        if any(marker in ua for marker in markers):
            return name
    return 'other'


def referrer_host(request):
    """The other site a visitor came from, as a bare host name; None for our own pages and anything odd."""
    try:
        host = urlsplit(request.META.get('HTTP_REFERER', '')).hostname
    except ValueError:
        return None
    if not host or len(host) > 80 or not HOST_RE.match(host) or LOCAL_HOST_RE.match(host):
        return None
    if host.startswith('www.'):
        host = host[4:]
    own = request.get_host().split(':')[0].lower()
    if host == (own[4:] if own.startswith('www.') else own):
        return None
    return host


class CacheRedis:
    """The few Redis commands used here, on top of the Django cache (development and tests without Redis)."""

    def pipeline(self, transaction=False):
        return CachePipeline(self)

    def pfadd(self, key, *members):
        cache.set(key, set(cache.get(key) or ()) | set(members), KEEP_DAYS)

    def pfcount(self, *keys):
        return len(set().union(*[cache.get(key) or set() for key in keys]))

    def hincrby(self, key, field, amount=1):
        data = dict(cache.get(key) or {})
        data[field] = data.get(field, 0) + amount
        cache.set(key, data, KEEP_DAYS)

    def hgetall(self, key):
        return dict(cache.get(key) or {})

    def zincrby(self, key, amount, member):
        self.hincrby(key, member, amount)

    def zrevrange(self, key, start, end, withscores=False):
        rows = sorted((cache.get(key) or {}).items(), key=lambda row: (row[1], row[0]), reverse=True)
        rows = rows[start:None if end == -1 else end + 1]
        return rows if withscores else [member for member, _ in rows]

    def zremrangebyrank(self, key, start, end):
        rows = sorted((cache.get(key) or {}).items(), key=lambda row: (row[1], row[0]))
        stop = len(rows) + end + 1 if end < 0 else end + 1
        if stop > start:
            cache.set(key, dict(rows[:start] + rows[stop:]), KEEP_DAYS)

    def expire(self, key, seconds):
        pass

    def set(self, key, value, nx=False):
        if not nx or cache.get(key) is None:
            cache.set(key, value, None)

    def get(self, key):
        return cache.get(key)


class CachePipeline:
    def __init__(self, client):
        self.client = client
        self.calls = []

    def __getattr__(self, name):
        def queue(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return self
        return queue

    def execute(self):
        calls, self.calls = self.calls, []
        return [getattr(self.client, name)(*args, **kwargs) for name, args, kwargs in calls]


def get_client():
    inner = getattr(cache, '_cache', None)
    getter = getattr(inner, 'get_client', None)
    return getter(write=True) if getter is not None else CacheRedis()


def _local(now):
    return datetime.fromtimestamp(time.time() if now is None else now, ZoneInfo(settings.DEFAULT_USER_TIME_ZONE))


def _day(date):
    return date.strftime('%Y%m%d')


def _text(value):
    return value.decode() if isinstance(value, bytes) else value


def _key(*parts):
    return PREFIX + ':'.join(str(part) for part in parts)


def track(request, member, kind, ref, is_page, now=None):
    """Count one visit (and a page view when is_page) in a single round trip."""
    ua = request.META.get('HTTP_USER_AGENT', '')
    guest = member[0] != 'u'
    if guest and not ua:
        return          # a real browser always names itself
    moment = _local(now)
    day, hour = _day(moment), '%02d' % moment.hour
    slot = (moment.hour * 60 + moment.minute) // SLOT_MINUTES
    pipe = get_client().pipeline(transaction=False)

    def unique(key, ttl):
        pipe.pfadd(key, member)
        pipe.expire(key, ttl)

    pipe.set(_key('since'), day, nx=True)
    unique(_key('g' if guest else 'u', day), KEEP_DAYS)
    unique(_key('hv', day, hour), KEEP_DETAIL)
    unique(_key('slot', day, slot), KEEP_SLOTS)
    unique(_key('dev', day, device_of(ua)), KEEP_DETAIL)
    unique(_key('br', day, browser_of(ua)), KEEP_DETAIL)
    if is_page:
        pipe.hincrby(_key('views', day), hour, 1)
        pipe.expire(_key('views', day), KEEP_DAYS)
        counted = [('pages', '%s|%s' % (kind, '' if kind == 'quiz' else ref))]
        source = referrer_host(request)
        if source:
            counted.append(('ref', source))
        for name, item in counted:
            pipe.zincrby(_key(name, day), 1, item)
            pipe.zremrangebyrank(_key(name, day), 0, -MAX_TRACKED - 1)
            pipe.expire(_key(name, day), KEEP_DETAIL)
    pipe.execute()


def _top(rows_per_day, limit):
    totals = {}
    for rows in rows_per_day:
        for item, score in rows:
            item = _text(item)
            totals[item] = totals.get(item, 0) + int(score)
    return sorted(totals.items(), key=lambda row: (-row[1], row[0]))[:limit]


class Batch:
    """Queues reads into one pipeline; ask() returns where the answer will be after run()."""

    def __init__(self):
        self.pipe = get_client().pipeline(transaction=False)
        self.size = 0

    def ask(self, name, *args, **kwargs):
        getattr(self.pipe, name)(*args, **kwargs)
        self.size += 1
        return self.size - 1

    def ask_hours(self, day):
        return [self.ask('pfcount', _key('hv', day, '%02d' % hour)) for hour in range(24)]

    def run(self):
        return self.pipe.execute()


def _peak(slots):
    """The busiest 5 minutes of the day and when they started."""
    peak = max(slots)
    start = slots.index(peak) * SLOT_MINUTES
    return {'peak': peak, 'peak_time': '%02d:%02d' % divmod(start, 60) if peak else None}


def _heat(dates, rows, moment):
    """Average unique visitors for each weekday and hour, over the days that were counted at all."""
    total = [[0] * 24 for _ in range(7)]
    samples = [[0] * 24 for _ in range(7)]
    for date, values in zip(dates, rows):
        if not any(values):
            continue
        weekday = date.weekday()
        for hour, value in enumerate(values):
            if date != moment.date() or hour <= moment.hour:    # hours still ahead say nothing yet
                total[weekday][hour] += value
                samples[weekday][hour] += 1
    return [[round(value / count, 1) if count else 0 for value, count in zip(*row)]
            for row in zip(total, samples)]


def _summary(row):
    return {'users': row['users'], 'guests': row['guests'], 'visitors': row['users'] + row['guests'],
            'views': row['views']}


def read(now=None):
    """All counters the dashboard shows, read in one pipeline. Page keys are still raw ('problem|code')."""
    moment = _local(now)
    dates = [moment.date() - timedelta(days=i) for i in range(HISTORY_DAYS - 1, -1, -1)]
    days = [_day(date) for date in dates]
    week = days[-7:]
    batch = Batch()
    since = batch.ask('get', _key('since'))
    per_day = [(batch.ask('pfcount', _key('u', d)), batch.ask('pfcount', _key('g', d)),
                batch.ask('hgetall', _key('views', d))) for d in days]
    periods = {name: [batch.ask('pfcount', *[_key(who, d) for d in span]) for who in ('u', 'g')]
               for name, span in (('week', week), ('month', days))}
    hourly = {d: batch.ask_hours(d) for d in days[-HEAT_DAYS:]}
    slots = [batch.ask('pfcount', _key('slot', days[-1], s)) for s in range(24 * 60 // SLOT_MINUTES)]
    tops = {name: [batch.ask('zrevrange', _key(name, d), 0, MAX_TRACKED - 1, withscores=True) for d in week]
            for name in ('pages', 'ref')}
    devices = {name: batch.ask('pfcount', *[_key('dev', d, name) for d in week]) for name in DEVICES}
    browsers = {name: batch.ask('pfcount', *[_key('br', d, name) for d in week]) for name in BROWSER_NAMES}
    result = batch.run()

    views = [{_text(k): int(v) for k, v in result[row[2]].items()} for row in per_day]
    history = [{'date': date.isoformat(), 'users': result[users], 'guests': result[guests],
                'views': sum(counts.values())}
               for date, (users, guests, _), counts in zip(dates, per_day, views)]
    hours = {d: [result[i] for i in asks] for d, asks in hourly.items()}
    first = _text(result[since])
    return {
        'since': datetime.strptime(str(first), '%Y%m%d').date().isoformat() if first else None,
        'today': dict(_summary(history[-1]), **_peak([result[i] for i in slots])),
        'yesterday': _summary(history[-2]),
        **{name: {'users': result[u], 'guests': result[g], 'visitors': result[u] + result[g]}
           for name, (u, g) in periods.items()},
        'days': history,
        'hours': {name: [{'visitors': value, 'views': views[back].get('%02d' % hour, 0)}
                         for hour, value in enumerate(hours[days[back]])]
                  for name, back in (('today', -1), ('yesterday', -2))},
        'heat': _heat(dates[-HEAT_DAYS:], [hours[d] for d in days[-HEAT_DAYS:]], moment),
        'pages': {'today': _top([result[tops['pages'][-1]]], MAX_TRACKED),
                  'week': _top([result[i] for i in tops['pages']], MAX_TRACKED)},
        'sources': {'today': _top([result[tops['ref'][-1]]], TOP),
                    'week': _top([result[i] for i in tops['ref']], TOP)},
        'devices': {name: result[i] for name, i in devices.items()},
        'browsers': sorted(((name, result[i]) for name, i in browsers.items() if result[i]),
                           key=lambda row: (-row[1], row[0])),
    }
