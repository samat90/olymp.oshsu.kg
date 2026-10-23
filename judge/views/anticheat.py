"""Tab-switch and paste tracking during a contest."""
import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.views.generic import DetailView
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from judge.models import ContestCheatEvent, ContestParticipation
from judge.utils.views import TitleMixin
from judge.views.contests import ContestMixin

# A tab switch usually fires both "blur" and "hidden"; events this close count once.
MERGE_SECONDS = 4


def anticheat_state(request):
    """Settings for the page script, or None when tracking does not apply."""
    participation = getattr(request, 'participation', None)
    if participation is None or not participation.live or participation.ended:
        return None
    contest = participation.contest
    if not contest.anticheat_enabled or participation.is_disqualified:
        return None
    if contest.is_editable_by(request.user) or contest.testers.filter(id=request.profile.id).exists():
        return None
    now = timezone.now()
    if participation.start > now:
        return None
    warnings = participation.cheat_events.filter(counted=True).count()
    return {
        'contest': contest.key,
        'warnings': warnings,
        'max': contest.anticheat_max_warnings,
    }


@login_required
@require_POST
def report(request, contest):
    participation = getattr(request, 'participation', None)
    if participation is None or participation.contest.key != contest:
        return JsonResponse({'ok': False, 'tracking': False})
    state = anticheat_state(request)
    if state is None:
        return JsonResponse({'ok': True, 'tracking': False, 'disqualified': participation.is_disqualified})

    try:
        data = json.loads(request.body or b'{}')
    except ValueError:
        data = {}
    kind = data.get('kind')
    if kind not in dict(ContestCheatEvent.KINDS):
        return JsonResponse({'ok': False, 'error': 'bad kind'}, status=400)
    detail = str(data.get('detail', ''))[:200]

    with transaction.atomic():
        # Lock the participation row so two quick events cannot both be the "last" warning.
        participation = ContestParticipation.objects.select_for_update().get(id=participation.id)
        last = participation.cheat_events.filter(counted=True).order_by('-time').first()
        now = timezone.now()
        counted = not (last and (now - last.time).total_seconds() < MERGE_SECONDS and kind != ContestCheatEvent.PASTE)
        ContestCheatEvent.objects.create(participation=participation, kind=kind, counted=counted, detail=detail,
                                         ip=request.META.get('REMOTE_ADDR'))
        warnings = participation.cheat_events.filter(counted=True).count()
        limit = participation.contest.anticheat_max_warnings
        disqualify = counted and warnings > limit and not participation.is_disqualified

    if disqualify:
        participation.set_disqualified(True)
    return JsonResponse({
        'ok': True,
        'tracking': True,
        'counted': counted,
        'warnings': warnings,
        'max': limit,
        'disqualified': disqualify or participation.is_disqualified,
    })


class ContestViolations(ContestMixin, TitleMixin, DetailView):
    template_name = 'contest/violations.html'

    def get_object(self, queryset=None):
        contest = super().get_object(queryset)
        if not contest.is_editable_by(self.request.user):
            raise Http404()
        return contest

    def get_title(self):
        return _('Violations in %s') % self.object.name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contest = self.object
        participations = (contest.users.filter(virtual=ContestParticipation.LIVE)
                          .select_related('user__user')
                          .annotate(warnings=Count('cheat_events', filter=Q(cheat_events__counted=True)),
                                    events=Count('cheat_events'))
                          .filter(events__gt=0)
                          .order_by('-is_disqualified', '-warnings', 'user__user__username'))
        by_participation = {}
        for event in ContestCheatEvent.objects.filter(participation__contest=contest).order_by('time'):
            by_participation.setdefault(event.participation_id, []).append(event)
        context['rows'] = [(p, by_participation.get(p.id, [])) for p in participations]
        return context
