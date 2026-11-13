from django.db import migrations

RANGES = ('1-8,11-13,15-18,20-28,30-39,41-60,63-68,71-83,88-98,109-198,209-298,303,309-342,'
          '344-398,404-498,504-548,552-648,650-668,670-678,684-878,883-887,889-928,934-1028')


def codes():
    result = []
    for part in RANGES.split(','):
        lo, _, hi = part.partition('-')
        result += ['%06d' % n for n in range(int(lo), int(hi or lo) + 1)]
    return result


def set_listed(value):
    def run(apps, schema_editor):
        apps.get_model('judge', 'Problem').objects.filter(code__in=codes()).update(is_listed=value)
    return run


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0180_show_all_problems_in_archive'),
    ]

    operations = [
        migrations.RunPython(set_listed(False), set_listed(True)),
    ]
