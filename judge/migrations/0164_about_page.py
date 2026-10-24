from django.db import migrations
from django.db.models import Max

OLD_MARK = '**C, C++, C# (Mono), Java 8, Python 3**'

ABOUT = """OshSU Olymp — сайт Ошского государственного университета, где студенты и школьники решают задачи по программированию и участвуют в олимпиадах. Его сделали на кафедре информационных систем и программирования МФТИТ.

Решать задачи можно на C, C++, C#, F#, Java, Python, JavaScript, Go, Kotlin, Pascal и Scratch. Решение отправляется прямо со страницы задачи, проверка занимает несколько секунд, а результат появляется в списке посылок сам, страницу обновлять не нужно.

На олимпиадах таблица результатов меняется по ходу соревнования, а после окончания организатор может скачать итоги в Excel. Чтобы всё было честно, сайт замечает, когда участник уходит со страницы олимпиады или вставляет код со стороны: сначала предупреждает, а после нескольких нарушений дисквалифицирует.

Для обычных занятий есть компилятор. В нём можно заводить проекты, хранить файлы и папки, запускать программы и вводить данные прямо в консоли. Компилятором можно пользоваться и во время олимпиады.

Ещё на сайте есть тренажёр слепой печати. Он учит печатать всеми пальцами, начиная с основного ряда клавиш и заканчивая цифрами, показывает скорость и точность и ведёт таблицу рекордов. Для программистов там есть отдельный режим, где печатаешь код.

Сайт работает на русском, кыргызском и английском языках.

С вопросами и предложениями пишите разработчику, Карабаеву С. Э., на skarabaev@oshsu.kg. Сайт университета: [oshsu.kg](https://oshsu.kg).
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
