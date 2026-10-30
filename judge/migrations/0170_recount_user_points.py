from django.core.cache import cache
from django.db import migrations


def recount(apps, schema_editor):
    """Every user's points and solved count are recounted from their submissions (some totals were stale)."""
    from judge.models import Profile

    for profile in Profile.objects.filter(submission__isnull=False).distinct().iterator():
        profile._updating_stats_only = True
        profile.calculate_points()
        cache.delete('user_complete:%d' % profile.id)
        cache.delete('user_attempted:%d' % profile.id)


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0169_all_problems_100_points'),
    ]

    operations = [
        migrations.RunPython(recount, migrations.RunPython.noop, elidable=True),
    ]
