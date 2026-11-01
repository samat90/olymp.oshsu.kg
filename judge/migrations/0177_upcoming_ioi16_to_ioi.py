from django.db import migrations


def to_legacy_ioi(apps, schema_editor):
    """Contests on the IOI 2016 format score unbatched problems by the worst test, so they get IOI (pre-2016).

    Only contests that have not started yet are switched; finished results stay as they were.
    """
    from django.utils import timezone

    Contest = apps.get_model('judge', 'Contest')
    Contest.objects.filter(format_name='ioi16', start_time__gt=timezone.now()).update(format_name='ioi')


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0176_partial_points_everywhere'),
    ]

    operations = [
        migrations.RunPython(to_legacy_ioi, migrations.RunPython.noop),
    ]
