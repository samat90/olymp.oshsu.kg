# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = {
    'title': 'ООП: классы и объекты',
    'lessons': [
        {
            'title': 'Классы и объекты',
            'blocks': [
                {
                    'type': 'text',
                    'text': r"""**Класс** — чертёж, **объект** — конкретный экземпляр по этому чертежу. Класс объединяет данные и функции для работы с ними.

Допустим, нужно хранить данные о лошадях: имя, возраст, усталость. Без классов пришлось бы заводить отдельные переменные для каждой лошади. С классом получается аккуратно:

```python
class Horse:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.tired = False

    def run(self, km):
        print(f"{self.name} пробежал {km} км")
        if km > 20:
            self.tired = True

    def rest(self):
        self.tired = False
        print(f"{self.name} отдыхает")

tulpar = Horse("Тулпар", 5)
akbar = Horse("Акбар", 7)
tulpar.run(25)
print(tulpar.tired)   # True
print(akbar.tired)    # False: у каждого объекта своё состояние
```

Разберём по частям:
- `class Horse:` объявляет класс. Названия классов принято писать с большой буквы.
- `__init__` — **конструктор**. Он вызывается автоматически при создании `Horse("Тулпар", 5)` и задаёт начальное состояние.
- `self` — «сам объект». Это первый параметр каждого метода; при вызове его не передают, Python подставляет сам.
- `self.name`, `self.age` — **атрибуты**: данные объекта.
- `run`, `rest` — **методы**: функции, принадлежащие классу.

### Атрибуты класса и объекта

```python
class Horse:
    species = "Equus caballus"      # одно значение на весь класс

    def __init__(self, name):
        self.name = name             # своё значение у каждого объекта
```

Атрибут класса общий для всех экземпляров, атрибут объекта (создаётся в `__init__` через `self`) — собственный.

### __str__

Если напечатать объект, получится что-то вроде `<__main__.Horse object at 0x7f...>`. Метод `__str__` задаёт понятное представление:

```python
class Horse:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"Конь {self.name}, {self.age} лет"

print(Horse("Тулпар", 5))   # Конь Тулпар, 5 лет
```

### Объекты внутри объектов

```python
class Caravan:
    def __init__(self):
        self.horses = []

    def add(self, horse):
        self.horses.append(horse)

    def oldest(self):
        return max(self.horses, key=lambda h: h.age)

c = Caravan()
c.add(Horse("Тулпар", 5))
c.add(Horse("Акбар", 7))
print(c.oldest())    # Конь Акбар, 7 лет
```

### Инкапсуляция

По соглашению атрибут с подчёркиванием в начале (`self._age`) считается внутренним, и снаружи его трогать не принято. Для проверок значений и вычисляемых атрибутов используют `property`:

```python
class Horse:
    def __init__(self, name, age):
        self.name = name
        self._age = age

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        if value < 0:
            raise ValueError("возраст не может быть отрицательным")
        self._age = value
```

Теперь `horse.age = 8` сработает, а `horse.age = -1` вызовет ошибку.

### Методы класса и статические методы

```python
class Horse:
    count = 0

    def __init__(self, name):
        self.name = name
        Horse.count += 1

    @classmethod
    def how_many(cls):
        return cls.count

    @staticmethod
    def is_adult(age):
        return age >= 3
```

`@classmethod` получает класс (`cls`), а не объект. `@staticmethod` — обычная функция, которая «живёт» внутри класса.

### Когда нужны классы

Когда есть сущность со своими данными и действиями: пользователь, заказ, игрок, фигура. Для маленьких скриптов классы не обязательны.""",
                },
                {
                    'type': 'text',
                    'title': 'Типичные ошибки',
                    'text': r"""- **Забыли `self`.** Метод `def run(km):` без `self` при вызове даст `TypeError: takes 1 positional argument but 2 were given`.
- **Забыли `self.` у атрибута.** В `__init__` запись `name = name` ничего не сохранит. Нужно `self.name = name`.
- **Изменяемый атрибут класса.** `items = []` на уровне класса — один список на все экземпляры. Создавайте списки в `__init__`.
- **Класс и объект.** `Horse` — класс, `Horse("Тулпар", 5)` — объект. Метод вызывают у объекта.
- **`__init__` не должен ничего возвращать.**
- **Опечатка в имени метода.** `__init_` или `__Init__` не будет вызван как конструктор, объект получится пустым.""",
                },
                {
                    'type': 'video',
                    'title': 'Видео: классы и объекты',
                    'video': 'https://www.youtube.com/watch?v=P4CNNo8jWj4',
                    'text': 'Первый урок серии про ООП: классы, объекты, атрибуты класса и объекта.',
                },
                {
                    'type': 'test',
                    'title': 'Проверка: классы',
                    'questions': [
                        Q('Что выведет программа?', ['Бобик Шарик', 'Шарик Шарик', 'Бобик Бобик', 'Ошибка'], 0, 'У каждого объекта свой атрибут `name`.', code=r"""class Dog:
    def __init__(self, name):
        self.name = name

a = Dog("Бобик")
b = Dog("Шарик")
print(a.name, b.name)"""),
                        Q('Что выведет программа?', ['3', '1', '0', 'Ошибка'], 0, '`inc` возвращает сам объект, поэтому вызовы можно «цеплять» друг за другом.', code=r"""class Counter:
    def __init__(self):
        self.n = 0

    def inc(self):
        self.n += 1
        return self

c = Counter()
c.inc().inc().inc()
print(c.n)"""),
                        Q('Что выведет программа?', ['[1]', '[]', 'Ошибка', 'None'], 0, 'Список — атрибут класса, он общий у всех экземпляров.', code=r"""class Box:
    items = []

a = Box()
b = Box()
a.items.append(1)
print(b.items)"""),
                        Q('Что выведет программа?', ["P(3) ['P(1)', 'P(2)']", '<P object> [...]', 'P(3) [P(1), P(2)]', 'Ошибка'], 0, '`print` вызывает `__str__`. Внутри списка отображаются строки с кавычками.', code=r"""class P:
    def __init__(self, x):
        self.x = x

    def __str__(self):
        return f"P({self.x})"

print(P(3), [str(P(1)), str(P(2))])"""),
                        Q('Что произойдёт?', ['TypeError: у метода нет параметра self', 'Выведет hi', 'Выведет None', 'Ничего не произойдёт'], 0, 'При вызове через объект Python передаёт объект первым аргументом, а в методе нет `self`.', code=r"""class A:
    def hello():
        print("hi")

A().hello()"""),
                    ],
                },
            ],
        },
        {
            'title': 'Практика: классы',
            'required': False,
            'blocks': [
                {
                    'type': 'text',
                    'text': 'Задачи сайта проверяют вывод, а не структуру, поэтому практика здесь — задание на проектирование. Если хотите потренироваться на задачах, возьмите уже решённые и оформите решение как класс с методами.',
                },
                {
                    'type': 'assignment',
                    'title': 'Банковский счёт',
                    'points': 10,
                    'text': r"""Создайте класс `Account`:
- атрибуты: владелец, баланс (через `property`, баланс не может быть отрицательным);
- методы: `deposit(amount)`, `withdraw(amount)` (при нехватке средств вызывает исключение), `__str__`;
- атрибут класса: сколько счетов создано.

Создайте два счёта, выполните несколько операций, обработайте ошибку при попытке снять больше, чем есть. Пришлите код и вывод.""",
                },
            ],
        },
    ],
}
