"""Touch-typing trainer: lessons, speed tests, code; results, records and levels."""
import json
import math
import secrets
import statistics
import time
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Max, Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from judge.models import Profile, TypingResult

LAYOUTS = [code for code, _name in TypingResult.LAYOUTS]
MODES = [code for code, _name in TypingResult.MODES]
MAX_CPM = 1000          # about the world record: not a human typing
MIN_SECONDS = 5
RECORDS_SHOWN = 50
PERIODS = {'day': timedelta(days=1), 'week': timedelta(days=7), 'month': timedelta(days=30), 'all': None}
RUN_TTL = 2 * 3600      # a started exercise can be saved within two hours
LESSON_PASS_ACCURACY = 93


def level_info(xp):
    """Level from the characters typed in checked results: level L starts at 500*L*(L-1) characters."""
    xp = int(xp or 0)
    level = int((1 + math.sqrt(1 + xp / 125)) / 2)
    start, end = 500 * level * (level - 1), 500 * (level + 1) * level
    return {'level': level, 'xp': xp, 'start': start, 'next': end,
            'percent': int(100 * (xp - start) / (end - start))}


def user_xp(profile):
    return (TypingResult.objects.filter(user=profile, checked=True, accuracy__gte=90)
            .aggregate(xp=Sum('chars'))['xp'] or 0)


def best_results(mode, layout, period='all', limit=RECORDS_SHOWN):
    """The best checked speed of every user (accuracy 90% and more), fastest first."""
    qs = TypingResult.objects.filter(mode=mode, layout=layout, accuracy__gte=90, checked=True)
    if mode == TypingResult.TEST:
        qs = qs.filter(seconds__gte=25)
    since = PERIODS.get(period)
    if since:
        qs = qs.filter(created__gte=timezone.now() - since)
    best = list(qs.values('user').annotate(best=Max('cpm')).order_by('-best')[:limit])
    if not best:
        return []
    ids = [b['user'] for b in best]
    profiles = {p.id: p for p in Profile.objects.filter(id__in=ids).select_related('user')}
    xp = dict(TypingResult.objects.filter(user_id__in=ids, checked=True, accuracy__gte=90)
              .values_list('user').annotate(xp=Sum('chars')))
    rows = []
    for place, b in enumerate(best, 1):
        result = qs.filter(user_id=b['user'], cpm=b['best']).order_by('created').first()
        rows.append({'place': place, 'profile': profiles[b['user']], 'cpm': b['best'], 'wpm': round(b['best'] / 5),
                     'level': level_info(xp.get(b['user']))['level'],
                     'accuracy': result.accuracy if result else None, 'date': result.created if result else None})
    return rows


def trainer(request):
    personal = {}
    history = []
    lessons = {}
    level = None
    if request.user.is_authenticated:
        for row in (TypingResult.objects.filter(user=request.profile, accuracy__gte=90, checked=True)
                    .values('mode', 'layout').annotate(best=Max('cpm'))):
            personal['%s-%s' % (row['mode'], row['layout'])] = row['best']
        history = list(TypingResult.objects.filter(user=request.profile)[:10])
        for layout, lesson, best in (TypingResult.objects
                                     .filter(user=request.profile, mode=TypingResult.LESSON,
                                             accuracy__gte=LESSON_PASS_ACCURACY, lesson__isnull=False)
                                     .values_list('layout', 'lesson').annotate(best=Max('cpm'))):
            lessons['%s:%d' % (layout, lesson)] = best
        level = level_info(user_xp(request.profile))
    return render(request, 'typing/index.html', {
        'title': _('Typing trainer'),
        'personal': personal,
        'history': history,
        'lessons_best': lessons,
        'level': level,
    })


def records(request):
    mode = request.GET.get('mode') if request.GET.get('mode') in (TypingResult.TEST, TypingResult.CODE) \
        else TypingResult.TEST
    layout = request.GET.get('layout') if request.GET.get('layout') in LAYOUTS else 'ru'
    period = request.GET.get('period') if request.GET.get('period') in PERIODS else 'week'
    key = 'typing-records2:%s:%s:%s' % (mode, layout, period)
    rows = cache.get(key)
    if rows is None:
        rows = best_results(mode, layout, period)
        cache.set(key, rows, 60)
    return render(request, 'typing/records.html', {
        'title': _('Typing records'),
        'rows': rows, 'mode': mode, 'layout': layout, 'period': period,
        'layouts': TypingResult.LAYOUTS,
        'my_id': request.profile.id if request.user.is_authenticated else None,
    })


@login_required
@require_POST
def start_run(request):
    """A one-time ticket for the exercise that starts now; the save must bring it back."""
    throttle = 'typing-start:%d' % request.profile.id
    count = cache.get_or_set(throttle, 0, 60)
    if count > 60:
        return JsonResponse({'ok': False}, status=429)
    cache.incr(throttle)
    token = secrets.token_urlsafe(16)
    cache.set('typing-run:' + token, {'user': request.profile.id, 'time': time.time()}, RUN_TTL)
    return JsonResponse({'ok': True, 'token': token})


def keystroke_problem(keys, chars, seconds):
    """Why the keystroke log does not look like a person typing, or None.

    keys holds the milliseconds before every typed character (the first one is 0).
    A paste or a script gives whole runs of zero gaps or perfectly even gaps.
    """
    if len(keys) != chars:
        return 'count'
    if any(k < 0 or k > 600000 for k in keys):
        return 'range'
    if sum(keys) > seconds * 1000 + 2000:
        return 'time'
    gaps = keys[1:]
    if len(gaps) < 10:
        return None
    if sum(1 for k in gaps if k < 20) > 0.2 * len(gaps):
        return 'burst'
    mean = statistics.fmean(gaps)
    if mean > 0 and len(gaps) >= 30 and statistics.pstdev(gaps) < 0.12 * mean:
        return 'even'
    return None


@login_required
@require_POST
def save_result(request):
    try:
        data = json.loads(request.body or b'{}')
        mode = str(data['mode'])
        layout = str(data['layout'])
        seconds = float(data['seconds'])
        chars = int(data['chars'])
        errors = int(data['errors'])
        lesson = int(data['lesson']) if data.get('lesson') is not None else None
        token = str(data.get('token') or '')
        keys = [int(k) for k in data.get('keys') or []][:20001]
    except (ValueError, KeyError, TypeError):
        return JsonResponse({'ok': False}, status=400)
    if mode not in MODES or layout not in LAYOUTS or not MIN_SECONDS <= seconds <= 3600 or \
            not 0 < chars <= 20000 or not 0 <= errors <= 20000 or (lesson is not None and not 0 <= lesson <= 100):
        return JsonResponse({'ok': False}, status=400)

    # Speed is counted here, from the characters and the time, not taken from the browser.
    cpm = round(chars * 60 / seconds)
    accuracy = round(100 * chars / (chars + errors), 1)
    if cpm > MAX_CPM:
        return JsonResponse({'ok': False, 'error': 'speed'}, status=400)
    throttle = 'typing-save:%d' % request.profile.id
    if not cache.add(throttle, 1, 3):
        return JsonResponse({'ok': False}, status=429)

    # The ticket proves the exercise really lasted that long; the keystroke log, that it was typed.
    run = cache.get('typing-run:' + token) if token else None
    if run:
        cache.delete('typing-run:' + token)
    if not run or run['user'] != request.profile.id:
        return JsonResponse({'ok': False, 'error': 'ticket'}, status=400)
    if time.time() - run['time'] + 2 < seconds:
        return JsonResponse({'ok': False, 'error': 'time'}, status=400)
    problem = keystroke_problem(keys, chars, seconds)
    if problem:
        return JsonResponse({'ok': False, 'error': 'typed', 'why': problem}, status=400)

    previous = (TypingResult.objects.filter(user=request.profile, mode=mode, layout=layout, accuracy__gte=90,
                                            checked=True).aggregate(best=Max('cpm'))['best'])
    xp_before = user_xp(request.profile)
    TypingResult.objects.create(user=request.profile, mode=mode, layout=layout, lesson=lesson, seconds=seconds,
                                chars=chars, errors=errors, cpm=cpm, accuracy=accuracy, checked=True)
    before, after = level_info(xp_before), level_info(user_xp(request.profile))
    return JsonResponse({'ok': True, 'cpm': cpm, 'accuracy': accuracy,
                         'record': accuracy >= 90 and (previous is None or cpm > previous), 'previous': previous,
                         'level': after, 'level_up': after['level'] > before['level']})
