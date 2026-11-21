from django.db import migrations, models


def fill_instructor(apps, schema_editor):
    Course = apps.get_model('judge', 'Course')
    for course in Course.objects.select_related('author__user').iterator():
        user = course.author.user
        name = ' '.join(part for part in (user.last_name.strip(), user.first_name.strip()) if part)
        if name:
            Course.objects.filter(id=course.id).update(instructor_name=name[:200])


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0187_course_auto_mode_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='instructor_name',
            field=models.CharField(blank=True, max_length=200,
                                   verbose_name='instructor (printed on the certificate)'),
        ),
        migrations.RunPython(fill_instructor, migrations.RunPython.noop),
    ]
