from django.db import migrations

LEGACY = ('MONOCS',)


def allow_all(apps, schema_editor):
    """Every problem allows every current language; Mono C# gives way to .NET C#.

    Only the allowed-language links change. Mono itself, its limits and old submissions stay."""
    alias = schema_editor.connection.alias
    Language = apps.get_model('judge', 'Language')
    Problem = apps.get_model('judge', 'Problem')
    links = Problem.allowed_languages.through.objects.using(alias)

    languages = list(Language.objects.using(alias).exclude(key__in=LEGACY).values_list('id', flat=True))
    problems = list(Problem.objects.using(alias).values_list('id', flat=True))
    existing = set(links.values_list('problem_id', 'language_id'))
    links.bulk_create([
        Problem.allowed_languages.through(problem_id=p, language_id=lang)
        for p in problems for lang in languages if (p, lang) not in existing
    ], batch_size=5000)

    if Language.objects.using(alias).filter(key='CSHARP').exists():
        links.filter(language__key__in=LEGACY).delete()


class Migration(migrations.Migration):
    dependencies = [('judge', '0164_about_page')]
    operations = [migrations.RunPython(allow_all, migrations.RunPython.noop)]
