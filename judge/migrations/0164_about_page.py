from django.db import migrations
from django.db.models import Max

OLD_MARK = '**C, C++, C# (Mono), Java 8, Python 3**'

ABOUT = """**OshSU Olymp** — платформа ОшГУ для олимпиад и занятий по программированию.

Разработана в Ошском государственном университете на кафедре информационных систем и программирования (ИСП) МФТИТ.

### Что есть на сайте

- **Задачи** с автоматической проверкой: решение отправляется из простой формы или из редактора на странице задачи.
- **Языки:** C, C++17, C++20, C# (.NET 10), Java, Python 3, JavaScript, Go, Kotlin, Pascal.
- **Посылки** обновляются сами: результат появляется сразу после проверки, свои посылки подсвечены.
- **Олимпиады** в форматах IOI, ACM/ICPC и AtCoder, табло в реальном времени, итоги в Excel.
- **Контроль на олимпиаде:** уход со страницы и вставка кода со стороны дают предупреждение, после нескольких предупреждений участник дисквалифицируется.
- **Компилятор** для повседневной работы: проекты, файлы и папки, запуск с вводом в консоли, форматирование кода, ссылки на код. Во время олимпиады он тоже доступен.
- **Три языка интерфейса:** русский, кыргызский, английский.

### Контакты

- **Разработчик:** Карабаев С. Э., кафедра ИСП МФТИТ ОшГУ
- **Email:** skarabaev@oshsu.kg
- **Сайт университета:** [oshsu.kg](https://oshsu.kg)
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
