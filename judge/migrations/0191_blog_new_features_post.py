from django.db import migrations
from django.utils import timezone

SLUG = 'novye-vozmozhnosti'
TITLE = 'Курсы, викторина, компилятор с подсказками и тысяча новых задач'

SUMMARY = ('За последние недели платформа заметно выросла: появились курсы с сертификатами, викторина для занятий, '
           'подсказки в компиляторе, более тысячи новых задач и 100-балльная система оценки.')

CONTENT = """За последние недели платформа заметно выросла. Коротко о том, что появилось, и где это искать.

## Курсы

В разделе [«Курсы»](/courses/) можно учиться в своём темпе: уроки с текстом, видео и формулами, тесты, задания, а в конце курса получить сертификат. Тесты и задания проверяются автоматически, прогресс сохраняется, к уроку можно вернуться в любой момент.

![Каталог курсов](/static/guide/shots/courses-catalog.jpg)

Сразу доступны готовые курсы: «Основы Python», «Основы C++», «Основы Java», «Основы C#», «Основы Go», «Основы JavaScript» и «Олимпиадное программирование».

Преподаватели могут создавать собственные курсы: добавлять уроки, тесты и задания, следить за успехами слушателей и выгружать таблицу в Excel. Чтобы получить статус преподавателя, напишите на [skarabaev@oshsu.kg](mailto:skarabaev@oshsu.kg).

Сертификат выдаётся после прохождения курса. У него свой номер вида OL26-000123-K7 и QR-код, по которому любой человек проверит, что сертификат настоящий. Его можно сохранить в PDF.

![Сертификат о прохождении курса](/static/guide/shots/s-certificate.jpg)

## Викторина

[Викторина](/quiz/) нужна для занятий: вопросы показываются на экране, а ответы приходят с телефонов. Достаточно навести камеру на QR-код или ввести PIN на странице olymp.oshsu.kg/quiz/join. Играть могут до 1000 человек одновременно, чем быстрее верный ответ, тем больше очков, а в конце показывается таблица лидеров.

![Экран ведущего](/static/guide/shots/q-host-lobby.jpg)

Свою викторину можно собрать вручную, загрузить из Excel или составить с помощью ИИ: нужно описать тему, а вопросы проверить и поправить. Типов вопросов двенадцать: от обычного выбора ответа до расстановки по порядку, облака слов и точки на картинке.

## Компилятор

В [компиляторе](/compiler/) появились подсказки при наборе кода. Он работает без регистрации, поддерживает проекты и файлы, интерактивный ввод с клавиатуры и ссылки, которыми можно поделиться. Языки: C, C++, C#, F#, Java, Python, JavaScript, Go, Kotlin, Pascal и Scratch.

![Компилятор с подсказками](/static/guide/shots/compiler-autocomplete.jpg)

## Тысяча новых задач и баллы

В [архиве](/problems/) добавлено более тысячи задач: от простых для первых шагов до олимпиадных. Теперь у каждой задачи 100 баллов, и они начисляются по доле пройденных тестов. Если решение пока неполное, вы всё равно видите, сколько тестов оно проходит, и можете улучшить его.

![Мои посылки с баллами](/static/guide/shots/submissions-mine.jpg)

## Дизайн и админка

Сайт получил новый современный вид и тёмную тему, а для администраторов и преподавателей переработана панель управления: понятнее таблицы и формы, проще найти нужные настройки.

## Руководство

Подробные инструкции со снимками экрана собраны на странице [«Руководство пользователя»](/guide/): как зарегистрироваться, отправить решение, пользоваться компилятором, участвовать в олимпиадах, создать и провести викторину, создать курс и получить сертификат.

Если что-то работает не так или не хватает какой-то возможности, пишите на [skarabaev@oshsu.kg](mailto:skarabaev@oshsu.kg).

---

**Кыргызча.** Платформада акыркы жумаларда көп жаңылык пайда болду: сертификаттуу [курстар](/courses/), сабактарга арналган [викторина](/quiz/), код терүүдө сунуш берген [компилятор](/compiler/), миңден ашык жаңы маселе жана ар бир маселеге 100 упай берүүчү система (упай өткөн тесттердин үлүшүнө жараша эсептелет). Сайттын көрүнүшү жана башкаруу панели жаңыртылды. Баары кадам-кадам [колдонмодо](/guide/) сүрөттөлгөн.

**English.** The platform has grown over the last weeks: [courses](/courses/) with certificates, a [quiz](/quiz/) for classes, a [compiler](/compiler/) with code suggestions, over a thousand new problems, and a 100-point scale where points follow the share of tests passed. The site has a new design and a reworked admin panel. Step-by-step instructions are in the [user guide](/guide/).
"""


def forward(apps, schema_editor):
    alias = schema_editor.connection.alias
    BlogPost = apps.get_model('judge', 'BlogPost')
    Profile = apps.get_model('judge', 'Profile')
    # Added once; a post that already exists (even edited or hidden by an administrator) is left alone.
    if BlogPost.objects.using(alias).filter(slug=SLUG).exists():
        return
    post = BlogPost.objects.using(alias).create(slug=SLUG, title=TITLE, visible=True, sticky=False,
                                                publish_on=timezone.now(), content=CONTENT, summary=SUMMARY)
    author = Profile.objects.using(alias).filter(user__username='samat1').first()
    if author is not None:
        post.authors.add(author)


class Migration(migrations.Migration):
    dependencies = [
        ('judge', '0190_guide_page'),
    ]
    operations = [migrations.RunPython(forward, migrations.RunPython.noop)]
