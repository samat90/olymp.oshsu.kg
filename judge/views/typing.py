"""Touch-typing trainer: lessons, speed tests, code; results and records."""
import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from judge.models import Profile, TypingResult

LAYOUTS = [code for code, _name in TypingResult.LAYOUTS]
MODES = [code for code, _name in TypingResult.MODES]
MAX_CPM = 1200          # faster than the world record: not a human typing
MIN_SECONDS = 5
RECORDS_SHOWN = 50
PERIODS = {'day': timedelta(days=1), 'week': timedelta(days=7), 'month': timedelta(days=30), 'all': None}


def best_results(mode, layout, period='all', limit=RECORDS_SHOWN):
    """The best speed of every user (accuracy 90% and more), fastest first."""
    qs = TypingResult.objects.filter(mode=mode, layout=layout, accuracy__gte=90)
    if mode == TypingResult.TEST:
        qs = qs.filter(seconds__gte=25)
    since = PERIODS.get(period)
    if since:
        qs = qs.filter(created__gte=timezone.now() - since)
    best = list(qs.values('user').annotate(best=Max('cpm')).order_by('-best')[:limit])
    if not best:
        return []
    profiles = {p.id: p for p in Profile.objects.filter(id__in=[b['user'] for b in best]).select_related('user')}
    rows = []
    for place, b in enumerate(best, 1):
        result = qs.filter(user_id=b['user'], cpm=b['best']).order_by('created').first()
        rows.append({'place': place, 'profile': profiles[b['user']], 'cpm': b['best'], 'wpm': round(b['best'] / 5),
                     'accuracy': result.accuracy if result else None, 'date': result.created if result else None})
    return rows


def trainer(request):
    personal = {}
    history = []
    if request.user.is_authenticated:
        for row in (TypingResult.objects.filter(user=request.profile, accuracy__gte=90)
                    .values('mode', 'layout').annotate(best=Max('cpm'))):
            personal['%s-%s' % (row['mode'], row['layout'])] = row['best']
        history = list(TypingResult.objects.filter(user=request.profile)[:10])
    return render(request, 'typing/index.html', {
        'title': _('Typing trainer'),
        'personal': personal,
        'history': history,
        'done_lessons': sorted(set(
            TypingResult.objects.filter(user=request.profile, mode=TypingResult.LESSON, accuracy__gte=93)
            .values_list('layout', 'lesson'))) if request.user.is_authenticated else [],
    })


def records(request):
    mode = request.GET.get('mode') if request.GET.get('mode') in (TypingResult.TEST, TypingResult.CODE) \
        else TypingResult.TEST
    layout = request.GET.get('layout') if request.GET.get('layout') in LAYOUTS else 'ru'
    period = request.GET.get('period') if request.GET.get('period') in PERIODS else 'week'
    key = 'typing-records:%s:%s:%s' % (mode, layout, period)
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
def save_result(request):
    try:
        data = json.loads(request.body or b'{}')
        mode = str(data['mode'])
        layout = str(data['layout'])
        seconds = float(data['seconds'])
        chars = int(data['chars'])
        errors = int(data['errors'])
        lesson = int(data['lesson']) if data.get('lesson') is not None else None
    except (ValueError, KeyError, TypeError):
        return JsonResponse({'ok': False}, status=400)
    if mode not in MODES or layout not in LAYOUTS or seconds < MIN_SECONDS or seconds > 3600 or \
            not 0 < chars <= 20000 or not 0 <= errors <= 20000 or (lesson is not None and not 0 <= lesson <= 100):
        return JsonResponse({'ok': False}, status=400)

    # Speed is counted here, from the characters and the time, not taken from the browser.
    cpm = round(chars * 60 / seconds)
    accuracy = round(100 * chars / (chars + errors), 1)
    if cpm > MAX_CPM:
        return JsonResponse({'ok': False}, status=400)
    throttle = 'typing-save:%d' % request.profile.id
    if not cache.add(throttle, 1, 3):
        return JsonResponse({'ok': False}, status=429)

    previous = (TypingResult.objects.filter(user=request.profile, mode=mode, layout=layout, accuracy__gte=90)
                .aggregate(best=Max('cpm'))['best'])
    TypingResult.objects.create(user=request.profile, mode=mode, layout=layout, lesson=lesson, seconds=seconds,
                                chars=chars, errors=errors, cpm=cpm, accuracy=accuracy)
    return JsonResponse({'ok': True, 'cpm': cpm, 'accuracy': accuracy,
                         'record': accuracy >= 90 and (previous is None or cpm > previous), 'previous': previous})
