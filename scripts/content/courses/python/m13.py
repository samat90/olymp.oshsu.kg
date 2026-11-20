MODULE = {
    'title': 'ООП: наследование, полиморфизм, магические методы',
    'lessons': [
        {'title': 'Наследование и полиморфизм', 'blocks': [
            {'type': 'text', 'title': 'Ат-Баши: семейство транспорта', 'text': """В Ат-Баши караван пополнился: теперь в нём не только лошади, но и яки, и повозка. У всех есть имя и способность двигаться, но движутся они по-разному. Писать почти одинаковый код для каждого вида скучно. **Наследование** позволяет вынести общее в «родительский» класс.

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
y.move()      # Борбой идёт  (метод унаследован)
y.carry()     # Борбой несёт 80 кг
print(h)      # Horse Тулпар
```

Главные идеи:
- `class Horse(Animal)` — `Horse` получает всё, что есть у `Animal`;
- метод можно **переопределить** в потомке;
- `super()` обращается к родителю: так не копируют его код.

Проверки: `isinstance(h, Animal)` — `True`, `issubclass(Horse, Animal)` — `True`.

### Полиморфизм: один вызов, разное поведение

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

Мы одинаково вызываем `move()` у разных объектов, а каждый делает своё. Цикл не знает и не должен знать, с каким именно животным он работает. Это и есть **полиморфизм**. Он избавляет от длинных `if type(x) == ...`.

В Python действует «утиная типизация»: *если оно ходит как утка и крякает как утка, значит это утка*. Объекту не нужно наследоваться от общего класса, достаточно, чтобы у него был нужный метод.

### Абстрактный базовый класс

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

### Композиция против наследования

Наследование выражает отношение «является»: конь *является* животным. Если отношение «имеет» (у каравана *есть* лошади), используйте композицию: храните объекты внутри другого объекта, как мы делали с `Caravan`. Не злоупотребляйте глубокими цепочками наследования: две-три ступени обычно достаточно.

### Множественное наследование

Python разрешает несколько родителей: `class C(A, B)`. Порядок поиска методов задаёт `C.__mro__`. Для начала лучше обходиться одним родителем.
"""},
            {'type': 'text', 'title': 'Ловушки: наследование', 'text': """- **Забыли `super().__init__()`** в конструкторе потомка: родительские атрибуты не создадутся, и вы получите `AttributeError`.
- **Опечатка в имени переопределённого метода.** Метод `moove` просто добавится как новый, а `move` останется родительским.
- **`isinstance` и точное сравнение типов.** `type(x) == Animal` не считает потомков, а `isinstance(x, Animal)` считает.
- **Слишком глубокая иерархия.** Если нужно прыгать между шестью файлами, чтобы понять метод, лучше упростить.
- **Изменение атрибута класса через объект.** `obj.species = "x"` создаёт новый атрибут у объекта и не меняет общий.
"""},
            {'type': 'video', 'title': 'Видео: наследование',
             'video': 'https://www.youtube.com/watch?v=4N4GSzLF7JM',
             'text': 'Урок канала itProger: наследование, инкапсуляция и полиморфизм.'},
            {'type': 'video', 'title': 'Видео: полиморфизм и абстрактные методы',
             'video': 'https://www.youtube.com/watch?v=fzUI3NyJflw',
             'text': 'Что такое полиморфизм и как его реализовать в Python (курс по ООП от selfedu).'},
            {'type': 'test', 'title': 'Проверка: наследование', 'questions': [
                {'text': 'Что выведет программа?', 'code': 'class A:\n    def hi(self):\n        return "A"\n\nclass B(A):\n    def hi(self):\n        return "B"\n\nprint(A().hi(), B().hi())', 'options': ['A B', 'A A', 'B B', 'B A'], 'answer': 0,
                 'expl': 'Метод `hi` переопределён в `B`.'},
                {'text': 'Что выведет программа?', 'code': 'class A:\n    def __init__(self):\n        self.x = 1\n\nclass B(A):\n    def __init__(self):\n        self.y = 2\n\nb = B()\nprint(hasattr(b, "x"), hasattr(b, "y"))', 'options': ['False True', 'True True', 'True False', 'False False'], 'answer': 0,
                 'expl': 'В `B.__init__` забыли вызвать `super().__init__()`, поэтому атрибут `x` не создался.'},
                {'text': 'Что выведет программа?', 'code': 'class A:\n    def who(self):\n        return "A"\n    def show(self):\n        return self.who()\n\nclass B(A):\n    def who(self):\n        return "B"\n\nprint(B().show())', 'options': ['B', 'A', 'AB', 'Ошибка'], 'answer': 0,
                 'expl': '`show` вызывает `self.who()`, а `self` — объект класса `B`, поэтому сработает переопределённый метод. Это и есть полиморфизм.'},
                {'text': 'Что выведет программа?', 'code': 'class A: pass\nclass B(A): pass\n\nb = B()\nprint(isinstance(b, A), type(b) == A)', 'options': ['True False', 'True True', 'False False', 'False True'], 'answer': 0,
                 'expl': '`isinstance` учитывает наследование, а `type(b) == A` сравнивает точный класс: он `B`.'},
                {'text': 'Что выведет программа?', 'code': 'class Shape:\n    def area(self):\n        raise NotImplementedError\n\nclass Sq(Shape):\n    def __init__(self, a):\n        self.a = a\n    def area(self):\n        return self.a ** 2\n\nprint(sum(s.area() for s in [Sq(2), Sq(3)]))', 'options': ['13', '25', '5', 'Ошибка'], 'answer': 0,
                 'expl': '`4 + 9 = 13`: для каждого объекта вызывается его собственный `area`.'},
            ]},
        ]},
        {'title': 'Магические методы', 'blocks': [
            {'type': 'text', 'title': 'Ат-Баши: когда объекты учатся складываться', 'text': """Нурзат заметила: числа можно складывать (`3 + 4`), строки склеивать (`"а" + "б"`), у списка есть длина (`len(a)`). А что если научить наши объекты тем же трюкам? Для этого существуют **магические методы** (dunder-методы, от *double underscore*): специальные имена с двумя подчёркиваниями с обеих сторон. Python вызывает их сам, когда вы применяете оператор или встроенную функцию.

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

Пример: класс «Деньги»:

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
print(a + b)         # 350 сом
print(a == Money(100))   # True
print(a < b)         # True
print(sorted([b, a]))    # [Money(100), Money(250)]
```

Раз у класса есть `__lt__`, обычная функция `sorted` умеет сортировать такие объекты. А для консоли и отладки полезен `__repr__`: он показывает объект «как в коде». Если `__str__` нет, `print` использует `__repr__`.

### Контейнер: __len__, __getitem__, __iter__

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
for city in r:           # работает: есть __getitem__
    print(city)
```

### Вызываемые объекты и контекст

Класс с `__call__` ведёт себя как функция. Классы с `__enter__` и `__exit__` работают в `with` (так устроен `open`). Это следующий уровень, к нему стоит вернуться позже.

### Меру знайте

Магические методы не должны удивлять. Если `a + b` у вас делает что-то совсем не похожее на сложение, читатель кода запутается. Используйте их, когда операция имеет очевидный смысл: сложить деньги, сравнить версии, измерить длину маршрута.
"""},
            {'type': 'text', 'title': 'Ловушки: магические методы', 'text': """- **`__eq__` без `__hash__`.** Если вы определили `__eq__`, объекты перестают быть хешируемыми: их нельзя положить в множество или использовать ключом словаря, пока не задан `__hash__`.
- **`__add__` и другой тип.** `Money(5) + 3` вызовет ошибку, если не проверить тип второго слагаемого. Возвращайте `NotImplemented` или поднимайте `TypeError`.
- **`__str__` должен возвращать строку**, а не печатать её.
- **Путаница `__str__` и `__repr__`.** `__str__` — для людей, `__repr__` — для разработчиков (однозначный, по возможности воспроизводящий объект).
- **Бесконечная рекурсия.** `__str__`, который делает `return str(self)`, зациклится.
- **Неправильное число подчёркиваний.** `_init_` или `__init_` — не конструктор.
"""},
            {'type': 'video', 'title': 'Видео: перегрузка операторов',
             'video': 'https://www.youtube.com/watch?v=sxuKZIcg96w',
             'text': 'Методы перегрузки операторов в классах: как научить объекты работать с `+`, `==` и другими операторами.'},
            {'type': 'test', 'title': 'Проверка: магические методы', 'questions': [
                {'text': 'Что выведет программа?', 'code': 'class V:\n    def __init__(self, x):\n        self.x = x\n    def __add__(self, other):\n        return V(self.x + other.x)\n    def __str__(self):\n        return f"V{self.x}"\n\nprint(V(1) + V(2) + V(3))', 'options': ['V6', 'V3', 'V123', 'Ошибка'], 'answer': 0,
                 'expl': 'Слева направо: `V(1) + V(2)` даёт `V(3)`, потом `V(3) + V(3)` даёт `V(6)`.'},
                {'text': 'Что выведет программа?', 'code': 'class R:\n    def __len__(self):\n        return 7\n\nprint(len(R()))', 'options': ['7', '0', 'Ошибка', 'R'], 'answer': 0,
                 'expl': '`len(x)` вызывает `x.__len__()`.'},
                {'text': 'Что выведет программа?', 'code': 'class P:\n    def __init__(self, n):\n        self.n = n\n    def __repr__(self):\n        return f"P({self.n})"\n\nprint([P(1), P(2)])', 'options': ['[P(1), P(2)]', '[<P object>, <P object>]', "['P(1)', 'P(2)']", 'Ошибка'], 'answer': 0,
                 'expl': 'Внутри списка Python показывает элементы через `__repr__`, а не `__str__`.'},
                {'text': 'Что выведет программа?', 'code': 'class N:\n    def __init__(self, v):\n        self.v = v\n    def __lt__(self, other):\n        return self.v < other.v\n\nprint([n.v for n in sorted([N(3), N(1), N(2)])])', 'options': ['[1, 2, 3]', '[3, 1, 2]', '[3, 2, 1]', 'Ошибка'], 'answer': 0,
                 'expl': '`sorted` использует `<`, то есть `__lt__`.'},
                {'text': 'Что выведет программа?', 'code': 'class A:\n    def __eq__(self, other):\n        return True\n\nprint(A() == A(), A() == 5, A() != 7)', 'options': ['True True False', 'True True True', 'False False False', 'True False True'], 'answer': 0,
                 'expl': '`__eq__` всегда возвращает `True`. А `!=` по умолчанию использует инверсию `__eq__`, то есть `False`.'},
            ]},
        ]},
        {'title': 'Практика: ООП', 'required': False, 'blocks': [
            {'type': 'text', 'title': 'Строим систему классов', 'text': """Лучшая практика для ООП — проект с несколькими взаимодействующими классами. Выберите тему сами, а ниже есть задание-образец. Не стремитесь к идеалу: главное — чтобы классы отражали понятия вашей задачи, а методы были маленькими и понятными.
"""},
            {'type': 'assignment', 'title': 'Задание: зоопарк фигур и животных', 'points': 10, 'text': """Часть 1 (наследование и полиморфизм). Создайте базовый класс `Shape` с методом `area()` и потомков `Circle`, `Rectangle`, `Triangle`. Составьте список разных фигур и выведите суммарную площадь и самую большую фигуру.

Часть 2 (магические методы). Создайте класс `Fraction` (дробь) с методами `__add__`, `__mul__`, `__eq__`, `__lt__`, `__str__`. Сложите 1/2 + 1/3 и убедитесь, что получилось 5/6 (при желании сокращайте дробь через `math.gcd`).

Пришлите код и вывод.
"""},
        ]},
    ],
}
