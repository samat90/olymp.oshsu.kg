"""Live "who is online and what are they doing" for the admins' home page.

Cheap by design: the middleware writes one small record per user into Redis (a single HASH member->"ts|kind|ref")
at most once per THROTTLE seconds per user and page, never touches the database, and any Redis error is swallowed.
The admin endpoint reads the HASH in one call and resolves user names with one query (result cached a few seconds).
"""
import time
import zlib

from django.core.cache import cache

HASH_KEY = 'olymp:online'
WINDOW = 120          # seconds a user counts as online after the last recorded request
THROTTLE = 20         # seconds between writes for the same user on the same page
PAYLOAD_TTL = 5       # seconds the built payload is shared between admins
NAMES_PER_GROUP = 40

BOT_MARKERS = ('bot', 'crawl', 'spider', 'slurp', 'monitor', 'uptime')

# kind -> sort order in the widget
KIND_ORDER = {'contest': 0, 'problem': 1, 'quiz': 2, 'compiler': 3, 'trainer': 4, 'browse': 5}

PAGE_LABELS = {
    'home': 'Главная',
    'problem_list': 'Задачи',
    'problem_random': 'Задачи',
    'contest_list': 'Соревнования',
    'contest_calendar': 'Соревнования',
    'user_list': 'Рейтинг',
    'user_ranking_redirect': 'Рейтинг',
    'user_page': 'Профили',
    'user_problems': 'Профили',
    'user_edit_profile': 'Профили',
    'organization_list': 'Организации',
    'organization_home': 'Организации',
    'about': 'О сайте',
    'blog_post': 'Новости',
    'ticket_list': 'Обращения',
    'ticket': 'Обращения',
    'typing_records': 'Рекорды тренажёра',
    'quiz_catalog': 'Каталог викторин',
    'quiz_my': 'Мои викторины',
    'quiz_join': 'Вход в викторину',
    'auth_login': 'Вход',
}
OTHER_LABEL = 'Другие страницы'


def classify(url_name, kwargs, in_contest=False, contest_id=None):
    """Map a resolved URL to (kind, ref); None when the request says nothing about what the user is doing."""
    if not url_name or url_name.startswith('online_'):
        return None
    if url_name == 'workspace' or url_name.startswith('workspace_'):
        return 'compiler', ''
    if url_name == 'typing' or url_name.startswith('typing_') and url_name != 'typing_records':
        return 'trainer', ''
    if url_name.startswith('quiz_'):
        if kwargs.get('pin'):
            return 'quiz', 'p:' + str(kwargs['pin'])
        if kwargs.get('key'):
            return 'quiz', 'k:' + str(kwargs['key'])
        if url_name == 'quiz_game_report' or url_name == 'quiz_game_report_xlsx':
            return 'browse', 'quiz_my'
        return 'browse', url_name
    if in_contest and contest_id is not None:
        return 'contest', 'i:%d' % contest_id
    if kwargs.get('contest') and url_name.startswith('contest_'):
        return 'contest', 'k:' + str(kwargs['contest'])
    if kwargs.get('problem') and url_name.startswith('problem_'):
        return 'problem', str(kwargs['problem'])
    return 'browse', url_name


class RedisBackend:
    def __init__(self, client):
        self.client = client

    def touch(self, member, value):
        pipe = self.client.pipeline(transaction=False)
        pipe.hset(HASH_KEY, member, value)
        pipe.expire(HASH_KEY, 3600)
        pipe.execute()

    def all(self):
        raw = self.client.hgetall(HASH_KEY)
        return {_text(k): _text(v) for k, v in raw.items()}

    def drop(self, members):
        if members:
            self.client.hdel(HASH_KEY, *members)


class CacheBackend:
    """Fallback for caches without Redis (development, tests): one dict under one key."""

    def touch(self, member, value):
        data = cache.get(HASH_KEY) or {}
        cutoff = time.time() - WINDOW
        data = {m: v for m, v in data.items() if _ts(v) >= cutoff}
        data[member] = value
        cache.set(HASH_KEY, data, 3600)

    def all(self):
        return dict(cache.get(HASH_KEY) or {})

    def drop(self, members):
        data = cache.get(HASH_KEY) or {}
        for member in members:
            data.pop(member, None)
        cache.set(HASH_KEY, data, 3600)


def _text(value):
    return value.decode() if isinstance(value, bytes) else value


def _ts(value):
    try:
        return float(value.split('|', 1)[0])
    except (ValueError, AttributeError):
        return 0.0


def get_backend():
    inner = getattr(cache, '_cache', None)
    getter = getattr(inner, 'get_client', None)
    if getter is not None:
        return RedisBackend(getter(write=True))
    return CacheBackend()


def member_for(request):
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated:
        return 'u%d' % user.pk
    ua = request.META.get('HTTP_USER_AGENT', '')
    if any(marker in ua.lower() for marker in BOT_MARKERS):
        return None
    ident = '%s|%s' % (request.META.get('REMOTE_ADDR', ''), ua)
    return 'g%08x' % zlib.crc32(ident.encode('utf-8', 'replace'))


def record(request, response):
    """Called by the middleware after the view ran. Never raises."""
    try:
        match = getattr(request, 'resolver_match', None)
        if match is None or request.method not in ('GET', 'HEAD', 'POST') or response.status_code >= 400:
            return
        name = match.url_name
        if name and name.startswith(('quiz_', 'workspace_', 'typing_')) and name != 'typing_records':
            pass  # polling/API calls of these tools are exactly the activity we want
        elif (request.method != 'GET' or request.headers.get('x-requested-with') == 'XMLHttpRequest' or
              not response.get('Content-Type', '').startswith('text/html')):
            return  # AJAX polls of ordinary pages and files say nothing about what the user is looking at
        participation = getattr(request, 'participation', None)
        kind = classify(name, match.kwargs, getattr(request, 'in_contest', False),
                        participation.contest_id if participation is not None else None)
        if kind is None:
            return
        member = member_for(request)
        if member is None:
            return
        value = '%d|%s|%s' % (time.time(), kind[0], kind[1])
        if not cache.add('olonl:%s:%08x' % (member, zlib.crc32(value.split('|', 1)[1].encode())), 1, THROTTLE):
            return
        get_backend().touch(member, value)
    except Exception:
        pass


def snapshot(now=None):
    """[(member, kind, ref)] for everybody seen within WINDOW; old records are dropped on the way."""
    backend = get_backend()
    now = time.time() if now is None else now
    alive, stale = [], []
    for member, value in backend.all().items():
        if _ts(value) >= now - WINDOW:
            parts = value.split('|', 2)
            if len(parts) == 3:
                alive.append((member, parts[1], parts[2]))
                continue
        stale.append(member)
    if stale:
        backend.drop(stale)
    return alive


def build_payload():
    """Aggregate the snapshot into the groups the widget shows. Needs the database for names."""
    from django.contrib.auth.models import User
    from django.urls import reverse

    from judge.models import Contest, GameSession, Problem, Quiz

    rows = snapshot()
    user_ids = [int(m[1:]) for m, _, _ in rows if m[0] == 'u']
    names = dict(User.objects.filter(id__in=user_ids).values_list('id', 'username'))

    problem_codes = {ref for _, kind, ref in rows if kind == 'problem'}
    problem_names = dict(Problem.objects.filter(code__in=problem_codes).values_list('code', 'name'))

    contest_keys = {ref[2:] for _, kind, ref in rows if kind == 'contest' and ref.startswith('k:')}
    contest_ids = {int(ref[2:]) for _, kind, ref in rows if kind == 'contest' and ref.startswith('i:')}
    contests = {}
    for key, name in Contest.objects.filter(key__in=contest_keys).values_list('key', 'name'):
        contests['k:' + key] = (key, name)
    for cid, key, name in Contest.objects.filter(id__in=contest_ids).values_list('id', 'key', 'name'):
        contests['i:%d' % cid] = (key, name)

    quiz_keys = {ref[2:] for _, kind, ref in rows if kind == 'quiz' and ref.startswith('k:')}
    pins = {ref[2:] for _, kind, ref in rows if kind == 'quiz' and ref.startswith('p:')}
    quizzes = {}
    for key, title in Quiz.objects.filter(key__in=quiz_keys).values_list('key', 'title'):
        quizzes['k:' + key] = (key, title)
    for pin, key, title in (GameSession.objects.filter(pin__in=pins).order_by('id')
                            .values_list('pin', 'quiz__key', 'quiz__title')):
        quizzes['p:' + pin] = (key, title)

    groups = {}

    def group(gid, kind, title, url):
        return groups.setdefault(gid, {'kind': kind, 'title': title, 'url': url, 'users': [], 'guests': 0})

    for member, kind, ref in rows:
        if kind == 'problem':
            g = group(('problem', ref), kind, 'Задача %s' % (problem_names.get(ref) or ref),
                      reverse('problem_detail', args=[ref]))
        elif kind == 'contest':
            key, name = contests.get(ref, (None, 'соревнование'))
            g = group(('contest', ref), kind, 'Соревнование: %s' % name,
                      reverse('contest_view', args=[key]) if key else None)
        elif kind == 'quiz':
            key, title = quizzes.get(ref, (None, None))
            g = group(('quiz', ref), kind, 'Викторина: %s' % title if title else 'Викторина',
                      reverse('quiz_detail', args=[key]) if key else None)
        elif kind == 'compiler':
            g = group(('compiler', ''), kind, 'Компилятор', reverse('workspace'))
        elif kind == 'trainer':
            g = group(('trainer', ''), kind, 'Тренажёр', reverse('typing'))
        else:
            label = PAGE_LABELS.get(ref, OTHER_LABEL)
            g = group(('browse', label), kind, 'Просматривают: %s' % label, None)
        if member[0] == 'u':
            g['users'].append(names.get(int(member[1:])) or '?')
        else:
            g['guests'] += 1

    out = []
    for g in groups.values():
        g['users'].sort(key=str.lower)
        g['count'] = len(g['users']) + g['guests']
        g['more'] = max(0, len(g['users']) - NAMES_PER_GROUP)
        g['users'] = g['users'][:NAMES_PER_GROUP]
        out.append(g)
    out.sort(key=lambda g: (KIND_ORDER[g['kind']], -g['count'], g['title']))
    total_users = sum(1 for m, _, _ in rows if m[0] == 'u')
    return {'total': len(rows), 'users': total_users, 'guests': len(rows) - total_users, 'groups': out}


def get_payload():
    data = cache.get('olonl:payload')
    if data is None:
        data = build_payload()
        cache.set('olonl:payload', data, PAYLOAD_TTL)
    return data
