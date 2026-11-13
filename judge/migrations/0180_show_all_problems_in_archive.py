from django.db import migrations


def show_all(apps, schema_editor):
    Problem = apps.get_model('judge', 'Problem')
    Problem.objects.filter(is_public=True, is_listed=False).update(is_listed=True)


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0179_typing_old_results_back'),
    ]

    operations = [
        migrations.RunPython(show_all, migrations.RunPython.noop),
    ]
