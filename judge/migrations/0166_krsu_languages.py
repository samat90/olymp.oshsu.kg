from django.db import migrations

NEW = [
    {'key': 'CPP14', 'name': 'GNU C++14', 'short_name': 'C++14', 'common_name': 'C++', 'ace': 'c_cpp',
     'pygments': 'cpp', 'extension': 'cpp',
     'template': '#include <iostream>\nusing namespace std;\n\nint main() {\n    long long a, b;\n'
                 '    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}\n'},
    {'key': 'CPP20', 'name': 'GNU C++20', 'short_name': 'C++20', 'common_name': 'C++', 'ace': 'c_cpp',
     'pygments': 'cpp', 'extension': 'cpp',
     'template': '#include <iostream>\nusing namespace std;\n\nint main() {\n    long long a, b;\n'
                 '    cin >> a >> b;\n    cout << a + b << endl;\n    return 0;\n}\n'},
    {'key': 'JAVA', 'name': 'Java 21', 'short_name': 'Java', 'common_name': 'Java', 'ace': 'java',
     'pygments': 'java', 'extension': 'java',
     'template': 'import java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n'
                 '        Scanner in = new Scanner(System.in);\n        long a = in.nextLong(), b = in.nextLong();\n'
                 '        System.out.println(a + b);\n    }\n}\n'},
    {'key': 'FSHARP', 'name': 'F# (.NET 10)', 'short_name': 'F#', 'common_name': 'F#', 'ace': 'fsharp',
     'pygments': 'fsharp', 'extension': 'fs',
     'template': 'let a = stdin.ReadLine().Split() |> Array.map int64\nprintfn "%d" (Array.sum a)\n'},
    {'key': 'SB3', 'name': 'Scratch 3', 'short_name': 'Scratch', 'common_name': 'Scratch', 'ace': 'text',
     'pygments': 'text', 'extension': 'sb3', 'template': '',
     'description': 'Отправьте файл проекта .sb3. Блок «спросить и ждать» читает строку ввода, '
                    '«сказать» печатает строку.'},
]

RENAME = {
    'CPP17': 'GNU C++17', 'GO': 'Go 1.25', 'KOTLIN': 'Kotlin 2.2', 'PAS': 'Free Pascal',
    'NODEJS': 'Node.js 22', 'C': 'GNU C11',
}

# Kept for old submissions only, like Mono C# before: one Java (21) in the list.
LEGACY = ('MONOCS', 'JAVA8')


def forward(apps, schema_editor):
    alias = schema_editor.connection.alias
    Language = apps.get_model('judge', 'Language')
    Problem = apps.get_model('judge', 'Problem')
    links = Problem.allowed_languages.through.objects.using(alias)
    problem_ids = list(Problem.objects.using(alias).values_list('pk', flat=True))

    for data in NEW:
        data = dict(data)
        language, _ = Language.objects.using(alias).update_or_create(key=data.pop('key'), defaults=data)
        links.bulk_create([links.model(problem_id=pk, language_id=language.pk) for pk in problem_ids],
                          ignore_conflicts=True, batch_size=5000)
    for key, name in RENAME.items():
        Language.objects.using(alias).filter(key=key).update(name=name)

    links.filter(language__key__in=LEGACY).delete()
    # Users whose default was Java 8 get Java 21.
    java = Language.objects.using(alias).get(key='JAVA')
    apps.get_model('judge', 'Profile').objects.using(alias).filter(language__key='JAVA8').update(language=java)


class Migration(migrations.Migration):
    dependencies = [('judge', '0165_all_languages_everywhere')]
    operations = [migrations.RunPython(forward, migrations.RunPython.noop)]
