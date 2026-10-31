from django.core.cache import cache
from django.db import migrations, models

BATCH = 1000


def to_partial(apps, schema_editor):
    """Every problem gives partial points: old submissions on all-or-nothing problems are rescored by passed tests.

    Contest problems and contest results are left as they were. Nothing is deleted.
    """
    # Recounting user points needs the model methods, so the real models are used.
    from judge.models import Problem, Profile, Submission

    problems = dict(Problem.objects.filter(partial=False).values_list('id', 'points'))
    Problem.objects.filter(id__in=problems).update(partial=True)

    changed = []
    subs = Submission.objects.filter(problem_id__in=problems, points__isnull=False, case_total__gt=0) \
                             .only('id', 'problem_id', 'case_points', 'case_total', 'points')
    for sub in subs.iterator(chunk_size=BATCH):
        points = round(sub.case_points / sub.case_total * problems[sub.problem_id], 3)
        if points != sub.points:
            sub.points = points
            changed.append(sub)
        if len(changed) >= BATCH:
            Submission.objects.bulk_update(changed, ['points'])
            changed = []
    if changed:
        Submission.objects.bulk_update(changed, ['points'])

    for profile in Profile.objects.filter(submission__isnull=False).distinct().iterator():
        profile._updating_stats_only = True
        profile.calculate_points()
        cache.delete('user_complete:%d' % profile.id)
        cache.delete('user_attempted:%d' % profile.id)


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0175_quiz_one_hosted_mode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='partial',
            field=models.BooleanField(default=True, verbose_name='allows partial points'),
        ),
        migrations.RunPython(to_partial, migrations.RunPython.noop, elidable=True),
    ]
