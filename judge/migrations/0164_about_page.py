from django.db import migrations
from django.db.models import Max

OLD_MARK = '**C, C++, C# (Mono), Java 8, Python 3**'

ABOUT = """OshSU Olymp — платформа Ошского государственного университета для олимпиад и занятий по программированию. Разработана на кафедре информационных систем и программирования МФТИТ.

На платформе собран архив задач с автоматической проверкой решений на C, C++, C#, F#, Java, Python, JavaScript, Go, Kotlin, Pascal и Scratch. Здесь проводятся олимпиады в форматах IOI, ACM/ICPC и AtCoder с контролем честности участников.

Для повседневной работы есть онлайн-компилятор с проектами и файлами и тренажёр слепой печати с уроками, тестами скорости и таблицей рекордов.

Интерфейс доступен на русском, кыргызском и английском языках.

Разработчик: Карабаев С. Э., skarabaev@oshsu.kg. Сайт университета: [oshsu.kg](https://oshsu.kg).
"""


def forward(apps, schema_editor):
    alias = schema_editor.connection.alias
    NavigationBar = apps.get_model('judge', 'NavigationBar')
    about = NavigationBar.objects.using(alias).filter(key='about', parent=None).first()
    if about is not None:
        # The navigation bar is ordered by tree; putting "About" in the last tree moves it to the end.
        last = NavigationBar.objects.using(alias).aggregate(m=Max('tree_id'))['m']
        if about.tree_id != last:
            NavigationBar.objects.using(alias).filter(tree_id=about.tree_id).update(tree_id=last + 1)

    FlatPage = apps.get_model('flatpages', 'FlatPage')
    page = FlatPage.objects.using(alias).filter(url='/about/').first()
    # Only the original text is replaced; a page someone already rewrote is left alone.
    if page is not None and OLD_MARK in page.content:
        page.content = ABOUT
        page.save()


class Migration(migrations.Migration):
    dependencies = [
        ('judge', '0163_compiler_navbar'),
        ('flatpages', '0001_initial'),
    ]
    operations = [migrations.RunPython(forward, migrations.RunPython.noop)]
