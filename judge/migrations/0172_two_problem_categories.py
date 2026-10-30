from django.db import migrations

# Only two categories are kept: training and olympiad problems.
MOVE = {
    'acmp': 'training',
    'kyrgyzstan': 'olympiad',
}


def merge_groups(apps, schema_editor):
    """Moves problems out of the extra categories, then drops those categories once they are empty."""
    Problem = apps.get_model('judge', 'Problem')
    ProblemGroup = apps.get_model('judge', 'ProblemGroup')

    for old, new in MOVE.items():
        source = ProblemGroup.objects.filter(name=old).first()
        target = ProblemGroup.objects.filter(name=new).first()
        if source is None or target is None:
            continue
        moved = Problem.objects.filter(group=source).update(group=target)
        print('  %s -> %s: %d problems' % (old, new, moved))
        # Problem.group cascades on delete, so a category is removed only when no problem is left in it.
        if not Problem.objects.filter(group=source).exists():
            source.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0171_problem_categories'),
    ]

    operations = [
        migrations.RunPython(merge_groups, migrations.RunPython.noop, elidable=True),
    ]
