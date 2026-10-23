from django.db import migrations

LANGUAGES = [
    {
        'key': 'NODEJS', 'name': 'JavaScript (Node.js)', 'short_name': 'JS', 'common_name': 'JavaScript',
        'ace': 'javascript', 'pygments': 'javascript', 'extension': 'js',
        'template': "const lines = require('fs').readFileSync(0, 'utf8').split('\\n');\n"
                    "const [a, b] = lines[0].split(' ').map(Number);\n"
                    "console.log(a + b);\n",
    },
    {
        'key': 'GO', 'name': 'Go', 'short_name': 'Go', 'common_name': 'Go',
        'ace': 'golang', 'pygments': 'go', 'extension': 'go',
        'template': 'package main\n\nimport (\n\t"bufio"\n\t"fmt"\n\t"os"\n)\n\nfunc main() {\n'
                    '\tin := bufio.NewReader(os.Stdin)\n\tvar a, b int\n\tfmt.Fscan(in, &a, &b)\n'
                    '\tfmt.Println(a + b)\n}\n',
    },
    {
        'key': 'KOTLIN', 'name': 'Kotlin', 'short_name': 'Kotlin', 'common_name': 'Kotlin',
        'ace': 'kotlin', 'pygments': 'kotlin', 'extension': 'kt',
        'template': 'fun main() {\n    val (a, b) = readln().split(" ").map { it.toLong() }\n    println(a + b)\n}\n',
    },
    {
        'key': 'PAS', 'name': 'Pascal (Free Pascal)', 'short_name': 'Pascal', 'common_name': 'Pascal',
        'ace': 'pascal', 'pygments': 'pascal', 'extension': 'pas',
        'template': 'var\n  a, b: int64;\nbegin\n  readln(a, b);\n  writeln(a + b);\nend.\n',
    },
]


def add_languages(apps, schema_editor):
    alias = schema_editor.connection.alias
    Language = apps.get_model('judge', 'Language')
    Problem = apps.get_model('judge', 'Problem')
    links = Problem.allowed_languages.through.objects.using(alias)
    problem_ids = list(Problem.objects.using(alias).values_list('pk', flat=True))
    for data in LANGUAGES:
        data = dict(data)
        language, _ = Language.objects.using(alias).update_or_create(key=data.pop('key'), defaults=data)
        links.bulk_create([links.model(problem_id=pk, language_id=language.pk) for pk in problem_ids],
                          ignore_conflicts=True)


def remove_languages(apps, schema_editor):
    apps.get_model('judge', 'Language').objects.using(schema_editor.connection.alias) \
        .filter(key__in=[lang['key'] for lang in LANGUAGES], submission__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [('judge', '0158_problem_code_alias')]
    operations = [migrations.RunPython(add_languages, remove_languages)]
