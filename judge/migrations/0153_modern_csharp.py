from django.db import migrations


def modern_csharp(apps, schema_editor):
    alias = schema_editor.connection.alias
    Language = apps.get_model('judge', 'Language')
    Problem = apps.get_model('judge', 'Problem')
    Profile = apps.get_model('judge', 'Profile')
    Limit = apps.get_model('judge', 'LanguageLimit')
    modern, _ = Language.objects.using(alias).update_or_create(key='CSHARP', defaults={
        'name': 'C# (.NET 10)', 'short_name': 'C#', 'common_name': 'C#',
        'ace': 'csharp', 'pygments': 'csharp', 'extension': 'cs', 'info': '',
        'template': 'using System;\n\nclass Program\n{\n    static void Main()\n    {\n        // Read input and write your answer here.\n    }\n}\n',
        'description': 'Microsoft .NET 10 / C# 14 (Roslyn). Submit one .cs file. '
                       'Both top-level statements and a static Main method are supported. '
                       'Standard .NET libraries are available; external NuGet packages are not.',
    })
    mono = Language.objects.using(alias).filter(key='MONOCS').first()
    if mono is None:
        return
    links = Problem.allowed_languages.through.objects.using(alias)
    for problem_id in list(links.filter(language_id=mono.pk).values_list('problem_id', flat=True)):
        links.get_or_create(problem_id=problem_id, language_id=modern.pk)
    for limit in Limit.objects.using(alias).filter(language_id=mono.pk):
        Limit.objects.using(alias).get_or_create(problem_id=limit.problem_id, language_id=modern.pk,
                                               defaults={'time_limit': limit.time_limit,
                                                         'memory_limit': limit.memory_limit})
    links.filter(language_id=mono.pk).delete()
    Profile.objects.using(alias).filter(language_id=mono.pk).update(language_id=modern.pk)
    # Keep Mono and its limits: historical submissions still refer to that runtime.


def restore_mono(apps, schema_editor):
    alias = schema_editor.connection.alias
    Language = apps.get_model('judge', 'Language')
    Problem = apps.get_model('judge', 'Problem')
    Profile = apps.get_model('judge', 'Profile')
    mono = Language.objects.using(alias).filter(key='MONOCS').first()
    modern = Language.objects.using(alias).filter(key='CSHARP').first()
    if mono is None or modern is None:
        return
    links = Problem.allowed_languages.through.objects.using(alias)
    for problem_id in list(links.filter(language_id=modern.pk).values_list('problem_id', flat=True)):
        links.get_or_create(problem_id=problem_id, language_id=mono.pk)
    links.filter(language_id=modern.pk).delete()
    Profile.objects.using(alias).filter(language_id=modern.pk).update(language_id=mono.pk)
    # Do not delete a language that may already have submissions.


class Migration(migrations.Migration):
    dependencies = [('judge', '0152_deactivate_user_permission')]
    operations = [migrations.RunPython(modern_csharp, restore_mono)]
