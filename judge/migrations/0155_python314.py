from django.db import migrations


def upgrade_python(apps, schema_editor):
    alias = schema_editor.connection.alias
    Language = apps.get_model('judge', 'Language')
    Problem = apps.get_model('judge', 'Problem')
    python = Language.objects.using(alias).get(key='PY3')
    python.name = 'Python 3.14'
    python.short_name = 'Py 3.14'
    python.save(using=alias, update_fields=['name', 'short_name'])
    links = Problem.allowed_languages.through.objects.using(alias)
    links.bulk_create([
        links.model(problem_id=pk, language_id=python.pk)
        for pk in Problem.objects.using(alias).exclude(allowed_languages=python).values_list('pk', flat=True)
    ], ignore_conflicts=True)


def restore_label(apps, schema_editor):
    apps.get_model('judge', 'Language').objects.using(schema_editor.connection.alias).filter(key='PY3').update(
        name='Python 3', short_name=None)


class Migration(migrations.Migration):
    dependencies = [('judge', '0154_csharp_all_problems')]
    operations = [migrations.RunPython(upgrade_python, restore_label)]
