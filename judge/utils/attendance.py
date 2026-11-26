"""The report behind the admins' attendance dashboard: Redis counters plus a few daily totals from the database."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone, translation

from judge.models import GameSession, Submission, TypingResult
from judge.utils import online, visit_stats

REPORT_TTL = 60         # the counters part is rebuilt at most once a minute
ACTIVITY_TTL = 600      # database totals at most once in ten minutes
ACTIVITY_DAYS = 30


def activity(now=None):
    """Per local day for the last ACTIVITY_DAYS: one grouped query per table, each over an indexed or small range."""
    zone = ZoneInfo(settings.DEFAULT_USER_TIME_ZONE)
    today = (now or timezone.now()).astimezone(zone).date()
    dates = [today - timedelta(days=i) for i in range(ACTIVITY_DAYS - 1, -1, -1)]
    start = datetime.combine(dates[0], datetime.min.time(), zone)

    def per_day(queryset, field, **counts):
        rows = (queryset.filter(**{field + '__gte': start})
                .annotate(day=TruncDate(field, tzinfo=zone))
                .values('day').annotate(**counts).order_by())
        return {row['day']: row for row in rows}

    tables = (
        (per_day(User.objects, 'date_joined', registrations=Count('id')), ('registrations',)),
        (per_day(Submission.objects, 'date', submissions=Count('id'), authors=Count('user', distinct=True)),
         ('submissions', 'authors')),
        (per_day(GameSession.objects, 'created', quiz_games=Count('id')), ('quiz_games',)),
        (per_day(TypingResult.objects, 'created', typing=Count('id')), ('typing',)),
    )
    out = []
    for date in dates:
        row = {'date': date.isoformat()}
        for found, names in tables:
            row.update({name: found.get(date, {}).get(name, 0) for name in names})
        out.append(row)
    return out


def get_activity():
    data = cache.get('olonl:activity')
    if data is None:
        data = activity()
        cache.set('olonl:activity', data, ACTIVITY_TTL)
    return data


def label_pages(rows, limit=visit_stats.TOP):
    """[('problem|code', views)] -> readable rows, pages with the same title added together."""
    pairs = [(tuple(key.split('|', 1)), views) for key, views in rows if '|' in key]
    describe = online.describer([pair for pair, _ in pairs])
    merged = {}
    for (kind, ref), views in pairs:
        _, title, url = describe(kind, ref, browse_prefix=False)
        page = merged.setdefault(title, {'title': title, 'url': url, 'kind': kind, 'views': 0})
        page['views'] += views
    return sorted(merged.values(), key=lambda page: (-page['views'], page['title']))[:limit]


def build_report():
    data = visit_stats.read()
    data['pages'] = {period: label_pages(rows) for period, rows in data['pages'].items()}
    data['activity'] = get_activity()
    data['generated'] = datetime.now(ZoneInfo(settings.DEFAULT_USER_TIME_ZONE)).strftime('%H:%M')
    return data


def get_report():
    key = 'olonl:report:%s' % translation.get_language()
    data = cache.get(key)
    if data is None:
        data = build_report()
        cache.set(key, data, REPORT_TTL)
    return data
