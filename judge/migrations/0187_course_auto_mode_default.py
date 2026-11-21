from django.db import migrations, models
from django.utils import timezone


def make_all_automatic(apps, schema_editor):
    """Every existing course goes automatic; the works waiting for a teacher count with full points."""
    alias = schema_editor.connection.alias
    apps.get_model('judge', 'Course').objects.using(alias).update(auto_mode=True)
    works = apps.get_model('judge', 'CourseWork').objects.using(alias).filter(
        status='pending', block__type='assignment').select_related('block')
    now = timezone.now()
    for work in works:
        work.status, work.grade, work.graded_at = 'graded', float(work.block.points), now
        work.save(update_fields=['status', 'grade', 'graded_at'])


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0186_course_auto_mode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='auto_mode',
            field=models.BooleanField(default=True, verbose_name='automatic mode'),
        ),
        migrations.RunPython(make_all_automatic, migrations.RunPython.noop),
    ]
