"""Publish problems once a scheduled contest has ended."""
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from judge.models import Contest, ContestProblem, Problem
from judge.signals import problem_update


def publish_finished_contest_problems(now=None):
    now = now or timezone.now()
    due = Contest.objects.filter(is_visible=True, publish_problems_after_end=True,
                                 end_time__lte=now, problems_published_at__isnull=True)
    result = {'contests': 0, 'problems': 0, 'waiting': 0}
    for contest_id in due.order_by('pk').values_list('pk', flat=True):
        with transaction.atomic():
            contest = Contest.objects.select_for_update().get(pk=contest_id)
            if (not contest.is_visible or not contest.publish_problems_after_end or
                    contest.end_time > now or contest.problems_published_at is not None):
                continue
            problems = list(Problem.objects.select_for_update().filter(
                pk__in=ContestProblem.objects.filter(contest=contest).values('problem_id')).order_by('pk'))
            pending = [p for p in problems if not p.is_public or not p.is_listed or p.is_organization_private]
            blocked = set(ContestProblem.objects.filter(
                problem_id__in=[p.pk for p in pending], contest__is_visible=True,
                contest__end_time__gt=now).values_list('problem_id', flat=True))
            published = []
            for problem in pending:
                if problem.pk in blocked:
                    continue
                problem.is_public = True
                problem.is_listed = True
                problem.is_organization_private = False
                if problem.date is None:
                    problem.date = contest.end_time
                published.append(problem)
            if published:
                Problem.objects.bulk_update(published, ['is_public', 'is_listed', 'is_organization_private', 'date'])
                for problem in published:
                    transaction.on_commit(lambda problem=problem: problem_update(Problem, problem))
                transaction.on_commit(lambda: cache.delete(
                    'hot_problems:86400:%d' % settings.DMOJ_PROBLEM_HOT_PROBLEM_COUNT))
            if not blocked:
                contest.problems_published_at = now
                contest.save(update_fields=['problems_published_at'])
                result['contests'] += 1
            result['problems'] += len(published)
            result['waiting'] += len(blocked)
    return result
