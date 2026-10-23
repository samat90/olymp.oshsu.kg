from django.db import migrations


def enable_csharp(apps, schema_editor):
    alias = schema_editor.connection.alias
    Language = apps.get_model('judge', 'Language')
    Problem = apps.get_model('judge', 'Problem')
    language = Language.objects.using(alias).get(key='CSHARP')
    links = Problem.allowed_languages.through.objects.using(alias)
    links.bulk_create([
        links.model(problem_id=pk, language_id=language.pk)
        for pk in Problem.objects.using(alias).exclude(allowed_languages=language).values_list('pk', flat=True)
    ], ignore_conflicts=True)


class Migration(migrations.Migration):
    dependencies = [('judge', '0153_modern_csharp')]
    # Existing access cannot be distinguished from newly granted access afterwards.
    # A reverse migration must not remove C# from previously enabled problems.
    operations = [migrations.RunPython(enable_csharp, migrations.RunPython.noop)]
