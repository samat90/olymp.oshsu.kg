# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Классы и свойства', pair(
    'Классы, свойства и конструкторы',
    r"""Класс описывает тип объектов: какие у них данные и что они умеют. Объект — экземпляр класса.

```csharp
class Horse
{
    private string name;
    private int age;

    public Horse(string name, int age)
    {
        this.name = name;
        this.age = age;
    }

    public string Name => name;
    public int Age => age;

    public void Birthday()
    {
        age++;
    }

    public override string ToString()
    {
        return $"{name}, {age} лет";
    }
}

Horse h = new Horse("Тулпар", 5);
h.Birthday();
Console.WriteLine(h);     // Тулпар, 6 лет
```

### Модификаторы доступа

`public` — доступно всем; `private` — только внутри класса (по умолчанию для членов класса); `protected` — классу и потомкам; `internal` — всей сборке. Данные скрывают, наружу выдают нужные методы и свойства. Это называется **инкапсуляцией**.

### Свойства

Свойство выглядит как поле, а работает как пара методов `get` и `set`:

```csharp
class Account
{
    private decimal balance;

    public decimal Balance
    {
        get { return balance; }
        private set
        {
            if (value < 0) throw new ArgumentException("баланс не может быть отрицательным");
            balance = value;
        }
    }

    public string Owner { get; set; }       // автосвойство: поле создаёт компилятор
    public int Id { get; } = 1;              // только чтение
}
```

Автосвойства `{ get; set; }` — самый частый вариант для хранения данных. Модификатор `private set` позволяет читать значение всем, а менять только классу.

### Инициализация объектов

```csharp
var h = new Horse("Тулпар", 5) { };
var a = new Account { Owner = "Нурзат" };   // инициализатор объекта
```

### Конструкторы

Конструкторов может быть несколько. Один может вызвать другой через `: this(...)`. Если конструктор не написан, создаётся пустой по умолчанию. Если написан хотя бы один с параметрами, пустой автоматически не создаётся.

### static

```csharp
class Counter
{
    public static int Count;
    public Counter() { Count++; }
}
new Counter(); new Counter();
Console.WriteLine(Counter.Count);   // 2
```

Статические члены принадлежат классу, а не объекту. `Main` тоже статический.

### class и struct

`class` — ссылочный тип: переменная хранит ссылку, при присваивании копируется ссылка. `struct` — тип значения: при присваивании копируется всё содержимое. Структуры подходят для небольших неизменяемых наборов данных (точка, цвет). Классы — для всего остального.

```csharp
struct Point { public int X, Y; }
Point p = new Point { X = 1, Y = 2 };
Point q = p;       // копия
q.X = 100;
Console.WriteLine(p.X);   // 1
```

### Ссылки и null

Переменная класса может быть `null`: вызов метода по ней даёт `NullReferenceException`. Проверяйте: `if (h != null)` или `h?.Birthday();`.

### Equals и GetHashCode

Оператор `==` для классов по умолчанию сравнивает ссылки. Чтобы сравнивать по содержимому, переопределяют `Equals`, а вместе с ним `GetHashCode`, иначе объекты будут вести себя неправильно в `Dictionary` и `HashSet`.

### Записи

В C# 9+ есть `record`: краткий способ объявить неизменяемый класс с сравнением по значению: `public record Point(int X, int Y);`.
""",
    r"""- **`NullReferenceException`.** Объект не создан или метод вернул `null`. Проверяйте перед использованием.
- **Забыли `this`.** В конструкторе `name = name;` присваивает параметр самому себе.
- **Публичные поля.** Любой может записать неверное значение. Используйте свойства.
- **Свойство обращается само к себе.** `public int X { get { return X; } }` — бесконечная рекурсия.
- **Копирование `struct` и `class`.** У класса копируется ссылка, у структуры данные. Это меняет поведение при присваивании.
- **Переопределили `Equals` без `GetHashCode`.** Предупреждение и ошибки в словарях.
- **Изменяемая структура в коллекции.** `list[0].X = 5` не работает для `struct`: изменится копия.
""",
    [
        Q('Что выведет программа?', ['Тулпар, 6 лет', 'Тулпар, 5 лет', 'Horse', 'Ошибка компиляции'], 0,
          '`ToString` определяет текстовое представление объекта.',
          code='class Horse\n{\n    string name; int age;\n    public Horse(string name, int age) { this.name = name; this.age = age; }\n    public void Birthday() { age++; }\n    public override string ToString() { return name + ", " + age + " лет"; }\n}\n\nclass P\n{\n    static void Main()\n    {\n        Horse h = new Horse("Тулпар", 5);\n        h.Birthday();\n        Console.WriteLine(h);\n    }\n}'),
        Q('Что выведет программа?', ['6 6', '5 6', '6 5', '5 5'], 0,
          'Для класса копируется ссылка: обе переменные указывают на один объект.',
          code='class Box { public int N = 5; }\n\nclass P\n{\n    static void Main()\n    {\n        Box a = new Box();\n        Box b = a;\n        b.N++;\n        Console.WriteLine(a.N + " " + b.N);\n    }\n}'),
        Q('Что выведет программа?', ['1 100', '100 100', '1 1', '100 1'], 0,
          '`struct` — тип значения: присваивание копирует данные, поэтому изменение копии не затрагивает оригинал.',
          code='struct Point { public int X; }\n\nclass P\n{\n    static void Main()\n    {\n        Point p = new Point { X = 1 };\n        Point q = p;\n        q.X = 100;\n        Console.WriteLine(p.X + " " + q.X);\n    }\n}'),
        Q('Что выведет программа?', ['3', '1', '0', '2'], 0,
          'Статическое поле общее для всех объектов.',
          code='class A\n{\n    public static int Count;\n    public A() { Count++; }\n}\n\nclass P\n{\n    static void Main()\n    {\n        new A(); new A(); new A();\n        Console.WriteLine(A.Count);\n    }\n}'),
        Q('Что выведет программа?', ['Нурзат 0', 'null 0', 'Нурзат', 'Ошибка компиляции'], 0,
          'Автосвойства и инициализатор объекта: свойству `Owner` присвоено значение, а число получило нуль по умолчанию.',
          code='class Account\n{\n    public string Owner { get; set; }\n    public int Id { get; set; }\n}\n\nclass P\n{\n    static void Main()\n    {\n        var a = new Account { Owner = "Нурзат" };\n        Console.WriteLine(a.Owner + " " + a.Id);\n    }\n}'),
        Q('Что произойдёт при компиляции?', ['Ошибка компиляции: приватное свойство недоступно для записи снаружи', 'Выведет 5', 'Выведет 0', 'Предупреждение'], 0,
          '`private set` разрешает менять значение только внутри класса.',
          code='class A\n{\n    public int X { get; private set; }\n}\n\nclass P\n{\n    static void Main()\n    {\n        var a = new A();\n        a.X = 5;\n        Console.WriteLine(a.X);\n    }\n}'),
    ],
    videos=[],
    practice=r"""Классы удобны для хранения связанных данных. Основное упражнение этого модуля — задание ниже.""",
    problems=[],
    task=('Банковский счёт', r"""Класс `Account`: владелец (свойство), баланс (`private set` с проверкой), конструктор, методы `Deposit`, `Withdraw` (бросает исключение при нехватке денег), `ToString`, статический счётчик созданных счетов. Переопределите `Equals` и `GetHashCode` по номеру счёта.

Создайте два счёта, выполните операции, покажите обработку ошибки. Пришлите код и вывод."""),
    short='классы'))
