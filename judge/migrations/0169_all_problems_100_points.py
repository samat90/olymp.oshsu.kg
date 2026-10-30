from django.core.cache import cache
from django.db import migrations, models, transaction


def to_100(apps, schema_editor):
    """Every problem and contest problem is worth 100 points; old submissions are rescored, nothing is deleted."""
    # Recalculation needs the model methods (contest formats, user points), so the real models are used.
    from judge.models import ContestParticipation, ContestProblem, ContestSubmission, Problem, Profile, Submission

    changed = list(Problem.objects.exclude(points=100).values_list('id', flat=True))
    Problem.objects.filter(id__in=changed).update(points=100)
    users = set()
    for problem in Problem.objects.filter(id__in=changed):
        for sub in Submission.objects.filter(problem=problem, points__isnull=False).only(
                'id', 'user_id', 'result', 'case_points', 'case_total', 'points').iterator():
            if sub.case_total:
                points = round(sub.case_points / sub.case_total * 100, 1)
            else:
                points = 100.0 if sub.result == 'AC' else 0.0
            if not problem.partial and points < 100:
                points = 0.0
            if points != sub.points:
                Submission.objects.filter(id=sub.id).update(points=points)
            users.add(sub.user_id)

    participations = set()
    for cp in ContestProblem.objects.exclude(points=100):
        cp.points = 100
        cp.save(update_fields=['points'])
        for cs in ContestSubmission.objects.filter(problem=cp).select_related('submission'):
            sub = cs.submission
            if sub.case_total:
                points = round(sub.case_points / sub.case_total * 100, 3)
            else:
                points = 100.0 if sub.result == 'AC' else 0.0
            if not cp.partial and points != 100:
                points = 0.0
            if points != cs.points:
                ContestSubmission.objects.filter(id=cs.id).update(points=points)
            participations.add(cs.participation_id)

    for participation in ContestParticipation.objects.filter(id__in=participations):
        try:
            with transaction.atomic():
                participation.recompute_results()
        except Exception as e:  # e.g. the MySQL-only "ioi16" format; the table can be rebuilt from the admin later
            print('  contest %s: results not recomputed (%s)' % (participation.contest.key, e))

    for profile in Profile.objects.filter(id__in=users):
        profile._updating_stats_only = True
        profile.calculate_points()
        cache.delete('user_complete:%d' % profile.id)
        cache.delete('user_attempted:%d' % profile.id)


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0168_profile_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contestproblem',
            name='points',
            field=models.IntegerField(default=100, verbose_name='points'),
        ),
        migrations.RunPython(to_100, migrations.RunPython.noop, elidable=True),
    ]
