# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = {
    'title': 'ООП: наследование, полиморфизм, магические методы',
    'lessons': [
        {
            'title': 'Наследование и полиморфизм',
            'blocks': [
                {
                    'type': 'text',
                    'text': r"""### Наследование

**Наследование** позволяет создать новый класс на основе существующего: он получает его данные и методы и может добавлять свои.

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def move(self):
        print(f"{self.name} идёт")

    def __str__(self):
        return f"{type(self).__name__} {self.name}"


class Horse(Animal):          # Horse наследует от Animal
    def move(self):            # переопределяем метод
        print(f"{self.name} скачет")


class Yak(Animal):
    def __init__(self, name, load):
        super().__init__(name)   # вызываем конструктор родителя
        self.load = load         # и добавляем своё

    def carry(self):
        print(f"{self.name} несёт {self.load} кг")


h = Horse("Тулпар")
y = Yak("Борбой", 80)
h.move()      # Тулпар скачет
y.move()      # Борбой идёт (метод унаследован)
y.carry()     # Борбой несёт 80 кг
print(h)      # Horse Тулпар
```

Главное:
- `class Horse(Animal)` — `Horse` получает всё, что есть у `Animal`;
- метод потомка с тем же именем **переопределяет** родительский;
- `super()` обращается к родителю, так не приходится копировать его код.

Проверки: `isinstance(h, Animal)` вернёт `True`, `issubclass(Horse, Animal)` тоже.

### Полиморфизм

Один и тот же вызов у разных объектов может делать разное:

```python
caravan = [Horse("Тулпар"), Yak("Борбой", 80), Animal("Кот")]
for animal in caravan:
    animal.move()
```

```
Тулпар скачет
Борбой идёт
Кот идёт
```

Цикл не знает, с каким именно животным работает, и не должен знать. Это и есть **полиморфизм**: он избавляет от длинных цепочек `if type(x) == ...`.

В Python действует «утиная типизация»: если у объекта есть нужный метод, его можно использовать, наследовать от общего класса необязательно.

### Абстрактные классы

Иногда родитель только задаёт «контракт», а реализация должна быть у потомков:

```python
class Shape:
    def area(self):
        raise NotImplementedError("потомок обязан реализовать area")

class Circle(Shape):
    def __init__(self, r):
        self.r = r
    def area(self):
        return 3.14159 * self.r ** 2
```

### Композиция

Наследование выражает отношение «является»: конь — животное. Если отношение «имеет» (у каравана есть лошади), используйте композицию: храните объекты внутри другого объекта, как в классе `Caravan`. Глубоких цепочек наследования избегайте: двух-трёх уровней обычно достаточно.

### Множественное наследование

Python допускает несколько родителей: `class C(A, B)`. Порядок поиска методов показывает `C.__mro__`. Для начала лучше обходиться одним родителем.""",
                },
                {
                    'type': 'text',
                    'title': 'Типичные ошибки',
                    'text': r"""- **Забыли `super().__init__()`** в конструкторе потомка: родительские атрибуты не создадутся, и вы получите `AttributeError`.
- **Опечатка в имени переопределяемого метода.** Метод `moove` просто добавится, а `move` останется родительским.
- **`type(x) == Animal` и `isinstance(x, Animal)`.** Первое не учитывает потомков, второе учитывает.
- **Слишком глубокая иерархия.** Если нужно прыгать между шестью файлами, чтобы понять метод, лучше упростить.
- **Изменение атрибута класса через объект.** `obj.species = "x"` создаёт новый атрибут у объекта и не меняет общий.""",
                },
                {
                    'type': 'video',
                    'title': 'Видео: наследование',
                    'video': 'https://www.youtube.com/watch?v=4N4GSzLF7JM',
                    'text': 'Урок канала itProger: наследование, инкапсуляция и полиморфизм.',
                },
                {
                    'type': 'video',
                    'title': 'Видео: полиморфизм и абстрактные методы',
                    'video': 'https://www.youtube.com/watch?v=fzUI3NyJflw',
                    'text': 'Что такое полиморфизм и как его реализовать в Python (курс по ООП от selfedu).',
                },
                {
                    'type': 'test',
                    'title': 'Проверка: наследование',
                    'questions': [
                        Q('Что выведет программа?', ['A B', 'A A', 'B B', 'B A'], 0, 'Метод `hi` переопределён в `B`.', code=r"""class A:
    def hi(self):
        return "A"

class B(A):
    def hi(self):
        return "B"

print(A().hi(), B().hi())"""),
                        Q('Что выведет программа?', ['False True', 'True True', 'True False', 'False False'], 0, 'В `B.__init__` забыли вызвать `super().__init__()`, поэтому атрибут `x` не создался.', code=r"""class A:
    def __init__(self):
        self.x = 1

class B(A):
    def __init__(self):
        self.y = 2

b = B()
print(hasattr(b, "x"), hasattr(b, "y"))"""),
                        Q('Что выведет программа?', ['B', 'A', 'AB', 'Ошибка'], 0, '`show` вызывает `self.who()`, а `self` — объект класса `B`, поэтому сработает переопределённый метод. Это и есть полиморфизм.', code=r"""class A:
    def who(self):
        return "A"
    def show(self):
        return self.who()

class B(A):
    def who(self):
        return "B"

print(B().show())"""),
                        Q('Что выведет программа?', ['True False', 'True True', 'False False', 'False True'], 0, '`isinstance` учитывает наследование, а `type(b) == A` сравнивает точный класс: он `B`.', code=r"""class A: pass
class B(A): pass

b = B()
print(isinstance(b, A), type(b) == A)"""),
                        Q('Что выведет программа?', ['13', '25', '5', 'Ошибка'], 0, '`4 + 9 = 13`: для каждого объекта вызывается его собственный `area`.', code=r"""class Shape:
    def area(self):
        raise NotImplementedError

class Sq(Shape):
    def __init__(self, a):
        self.a = a
    def area(self):
        return self.a ** 2

print(sum(s.area() for s in [Sq(2), Sq(3)]))"""),
                    ],
                },
            ],
        },
        {
            'title': 'Магические методы',
            'blocks': [
                {
                    'type': 'text',
                    'text': r"""Числа можно складывать, у списка есть длина, строку можно сравнить с другой. Свои объекты можно научить тому же. Для этого служат **магические методы** (dunder-методы, от англ. *double underscore*): специальные имена с двумя подчёркиваниями с каждой стороны. Python сам вызывает их, когда вы применяете оператор или встроенную функцию.

| выражение | какой метод вызывается |
|---|---|
| `Money(5)` | `__init__` |
| `str(x)`, `print(x)` | `__str__` |
| `repr(x)` | `__repr__` |
| `a + b` | `__add__` |
| `a == b` | `__eq__` |
| `a < b` | `__lt__` |
| `len(x)` | `__len__` |
| `x[i]` | `__getitem__` |
| `x in c` | `__contains__` |
| `for i in x` | `__iter__` |
| `x()` | `__call__` |

Пример — класс «Деньги»:

```python
class Money:
    def __init__(self, amount):
        self.amount = amount

    def __str__(self):
        return f"{self.amount} сом"

    def __repr__(self):
        return f"Money({self.amount})"

    def __add__(self, other):
        return Money(self.amount + other.amount)

    def __eq__(self, other):
        return self.amount == other.amount

    def __lt__(self, other):
        return self.amount < other.amount


a = Money(100)
b = Money(250)
print(a + b)             # 350 сом
print(a == Money(100))   # True
print(a < b)             # True
print(sorted([b, a]))    # [Money(100), Money(250)]
```

Раз у класса есть `__lt__`, функция `sorted` умеет сортировать такие объекты. Для консоли и отладки полезен `__repr__`: он показывает объект «как в коде». Если нет `__str__`, `print` использует `__repr__`.

### Контейнер: __len__, __getitem__

```python
class Route:
    def __init__(self, *cities):
        self.cities = list(cities)

    def __len__(self):
        return len(self.cities)

    def __getitem__(self, i):
        return self.cities[i]

    def __contains__(self, city):
        return city in self.cities

r = Route("Бишкек", "Каракол", "Ош")
print(len(r))            # 3
print(r[1])              # Каракол
print("Ош" in r)         # True
for city in r:           # работает благодаря __getitem__
    print(city)
```

### Вызываемые объекты и контекст

Объект класса с методом `__call__` можно вызывать как функцию. Методы `__enter__` и `__exit__` позволяют использовать объект в `with` (так устроен `open`). Это следующий уровень, к нему стоит вернуться позже.

### Меру знайте

Магические методы не должны удивлять. Если `a + b` делает что-то совсем не похожее на сложение, код становится трудным для чтения. Применяйте их там, где операция очевидна: сложить деньги, сравнить версии, узнать длину маршрута.""",
                },
                {
                    'type': 'text',
                    'title': 'Типичные ошибки',
                    'text': r"""- **`__eq__` без `__hash__`.** Если определить `__eq__`, объекты перестают быть хешируемыми: их нельзя класть в множество и использовать ключами словаря, пока не задан `__hash__`.
- **`__add__` и другой тип.** `Money(5) + 3` вызовет ошибку, если не проверить тип второго слагаемого. Возвращайте `NotImplemented` или вызывайте `TypeError`.
- **`__str__` должен возвращать строку,** а не печатать её.
- **`__str__` и `__repr__`.** Первый для людей, второй для разработчиков (однозначный и, по возможности, воспроизводящий объект).
- **Бесконечная рекурсия.** `__str__`, который делает `return str(self)`, зациклится.
- **Неверное число подчёркиваний.** `_init_` или `__init_` — не конструктор.""",
                },
                {
                    'type': 'video',
                    'title': 'Видео: перегрузка операторов',
                    'video': 'https://www.youtube.com/watch?v=sxuKZIcg96w',
                    'text': 'Методы перегрузки операторов в классах: как научить объекты работать с `+`, `==` и другими операторами.',
                },
                {
                    'type': 'test',
                    'title': 'Проверка: магические методы',
                    'questions': [
                        Q('Что выведет программа?', ['V6', 'V3', 'V123', 'Ошибка'], 0, 'Слева направо: `V(1) + V(2)` даёт `V(3)`, потом `V(3) + V(3)` даёт `V(6)`.', code=r"""class V:
    def __init__(self, x):
        self.x = x
    def __add__(self, other):
        return V(self.x + other.x)
    def __str__(self):
        return f"V{self.x}"

print(V(1) + V(2) + V(3))"""),
                        Q('Что выведет программа?', ['7', '0', 'Ошибка', 'R'], 0, '`len(x)` вызывает `x.__len__()`.', code=r"""class R:
    def __len__(self):
        return 7

print(len(R()))"""),
                        Q('Что выведет программа?', ['[P(1), P(2)]', '[<P object>, <P object>]', "['P(1)', 'P(2)']", 'Ошибка'], 0, 'Внутри списка Python показывает элементы через `__repr__`, а не `__str__`.', code=r"""class P:
    def __init__(self, n):
        self.n = n
    def __repr__(self):
        return f"P({self.n})"

print([P(1), P(2)])"""),
                        Q('Что выведет программа?', ['[1, 2, 3]', '[3, 1, 2]', '[3, 2, 1]', 'Ошибка'], 0, '`sorted` использует `<`, то есть `__lt__`.', code=r"""class N:
    def __init__(self, v):
        self.v = v
    def __lt__(self, other):
        return self.v < other.v

print([n.v for n in sorted([N(3), N(1), N(2)])])"""),
                        Q('Что выведет программа?', ['True True False', 'True True True', 'False False False', 'True False True'], 0, '`__eq__` всегда возвращает `True`. А `!=` по умолчанию использует инверсию `__eq__`, то есть `False`.', code=r"""class A:
    def __eq__(self, other):
        return True

print(A() == A(), A() == 5, A() != 7)"""),
                    ],
                },
            ],
        },
        {
            'title': 'Практика: ООП',
            'required': False,
            'blocks': [
                {
                    'type': 'text',
                    'text': 'Лучшая практика для ООП — проект из нескольких взаимодействующих классов. Не гонитесь за идеалом: классы должны отражать понятия вашей задачи, а методы быть небольшими и понятными.',
                },
                {
                    'type': 'assignment',
                    'title': 'Фигуры и дроби',
                    'points': 10,
                    'text': r"""Часть 1 (наследование и полиморфизм). Создайте базовый класс `Shape` с методом `area()` и потомков `Circle`, `Rectangle`, `Triangle`. Составьте список разных фигур и выведите суммарную площадь и самую большую фигуру.

Часть 2 (магические методы). Создайте класс `Fraction` (дробь) с методами `__add__`, `__mul__`, `__eq__`, `__lt__`, `__str__`. Сложите 1/2 и 1/3 и убедитесь, что получилось 5/6 (при желании сокращайте дробь через `math.gcd`).

Пришлите код и вывод.""",
                },
            ],
        },
    ],
}
