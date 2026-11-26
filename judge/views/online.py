import functools
import json
import logging

from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from judge.utils import attendance, online

logger = logging.getLogger('judge.attendance')


def admins_only(view):
    """Live and attendance statistics are for the site staff; everybody else gets a plain 404."""
    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not (user.is_authenticated and (user.is_superuser or user.is_staff)):
            raise Http404()
        return view(request, *args, **kwargs)
    return wrapper


@never_cache
@admins_only
def online_now(request):
    return JsonResponse(online.get_payload(), json_dumps_params={'ensure_ascii': False})


def chart_labels():
    return {
        'visitors': _('Visitors'),
        'users': _('Signed in'),
        'guests': _('Guests'),
        'views': _('Page views'),
        'today': _('Today'),
        'yesterday': _('Yesterday'),
        'peak': _('Peak (5 min)'),
        'week': _('7 days'),
        'month': _('30 days'),
        'registrations': _('Registrations'),
        'submissions': _('Submissions'),
        'authors': _('Authors'),
        'quiz_games': _('Quiz games'),
        'typing': _('Typing runs'),
        'desktop': _('Computer'),
        'mobile': _('Phone'),
        'tablet': _('Tablet'),
        'other': _('Other'),
        'since': _('Counted since'),
        'updated': _('Updated'),
        'empty': _('No data yet'),
        'failed': _('Statistics are unavailable'),
        'date': _('Date'),
        # Monday first, like date.weekday()
        'weekdays': [_('Mon'), _('Tue'), _('Wed'), _('Thu'), _('Fri'), _('Sat'), _('Sun')],
    }


@never_cache
@admins_only
def online_dashboard(request):
    return render(request, 'attendance/dashboard.html', {
        'title': _('Attendance'),
        'chart_labels': json.dumps(chart_labels(), ensure_ascii=False),
    })


@never_cache
@admins_only
def online_dashboard_data(request):
    try:
        data = attendance.get_report()
    except Exception:
        logger.exception('attendance report failed')
        return JsonResponse({'error': 'unavailable'}, status=503)
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
