# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Методы', pair(
    'Методы',
    r"""В C# функции называются **методами** и всегда принадлежат классу.

```csharp
class Program
{
    static int Area(int w, int h)
    {
        return w * h;
    }

    static void Main()
    {
        Console.WriteLine(Area(4, 5));
    }
}
```

Объявление: модификаторы, тип результата, имя, параметры. Метод, ничего не возвращающий, имеет тип `void`. Короткие методы можно записывать так: `static int Area(int w, int h) => w * h;`.

### Передача параметров

По умолчанию аргументы передаются **по значению** (копируются):

```csharp
static void Inc(int x) { x++; }
int a = 5;
Inc(a);
Console.WriteLine(a);   // 5
```

Если метод должен изменить переменную, используют `ref` или `out`:

```csharp
static void IncRef(ref int x) { x++; }

static bool TryDivide(int a, int b, out int result)
{
    if (b == 0) { result = 0; return false; }
    result = a / b;
    return true;
}

int n = 5;
IncRef(ref n);                 // n == 6
if (TryDivide(7, 2, out int q))
    Console.WriteLine(q);      // 3
```

- `ref` — переменная должна быть инициализирована до вызова, метод может её изменить;
- `out` — метод **обязан** присвоить значение, инициализировать заранее не нужно.

Объекты (массивы, списки, классы) передаются по значению ссылки: метод может изменять содержимое объекта, но не может заставить внешнюю переменную указывать на другой объект (без `ref`).

### Необязательные и именованные параметры

```csharp
static int Power(int b, int exp = 2)
{
    int r = 1;
    for (int i = 0; i < exp; i++) r *= b;
    return r;
}

Power(3);            // 9
Power(2, 10);        // 1024
Power(exp: 3, b: 2); // 8: именованные аргументы
```

### Перегрузка

Несколько методов с одним именем, но разными параметрами:

```csharp
static int Add(int a, int b) => a + b;
static double Add(double a, double b) => a + b;
```

### params

```csharp
static int Sum(params int[] nums)
{
    int total = 0;
    foreach (int n in nums) total += n;
    return total;
}
Sum();          // 0
Sum(1, 2, 3);   // 6
```

### Несколько результатов: кортежи

```csharp
static (int, int) DivMod(int a, int b) => (a / b, a % b);

var (q, r) = DivMod(17, 5);
Console.WriteLine(q + " " + r);     // 3 2
```

### Рекурсия

```csharp
static long Fact(int n) => n <= 1 ? 1 : n * Fact(n - 1);
```

Очень глубокая рекурсия приводит к `StackOverflowException`, который нельзя перехватить.

### Локальные функции

Метод можно объявить внутри другого метода:

```csharp
static int Sum(int[] a)
{
    int Square(int x) => x * x;
    return a.Select(Square).Sum();
}
```
""",
    r"""- **Ожидание, что метод изменит число.** Передаётся копия. Верните результат или используйте `ref`.
- **`out` без присваивания.** Метод обязан задать значение на всех путях.
- **Присваивание параметру-ссылке** внутри метода не влияет на внешнюю переменную без `ref`.
- **Метод без `return`** для не-`void` — ошибка компиляции.
- **Рекурсия без базового случая.** `StackOverflowException` завершает программу.
- **Порядок именованных параметров** можно менять, но смешивать их с позиционными нужно аккуратно.
""",
    [
        Q('Что выведет программа?', ['5 6', '6 6', '5 5', '6 5'], 0,
          'Первый вызов меняет копию, второй (`ref`) — оригинал.',
          code='class P\n{\n    static void Inc(int x) { x++; }\n    static void IncRef(ref int x) { x++; }\n    static void Main()\n    {\n        int a = 5;\n        Inc(a);\n        Console.Write(a + " ");\n        IncRef(ref a);\n        Console.WriteLine(a);\n    }\n}'),
        Q('Что выведет программа?', ['9 1024', '9 9', '6 20', '3 10'], 0,
          'Если второй аргумент не указан, используется значение по умолчанию 2.',
          code='class P\n{\n    static int Power(int b, int exp = 2)\n    {\n        int r = 1;\n        for (int i = 0; i < exp; i++) r *= b;\n        return r;\n    }\n    static void Main()\n    {\n        Console.WriteLine(Power(3) + " " + Power(2, 10));\n    }\n}'),
        Q('Что выведет программа?', ['3 2', '2 3', '3.4 2', '17 5'], 0,
          'Метод возвращает кортеж из частного и остатка.',
          code='class P\n{\n    static (int, int) DivMod(int a, int b) => (a / b, a % b);\n    static void Main()\n    {\n        var (q, r) = DivMod(17, 5);\n        Console.WriteLine(q + " " + r);\n    }\n}'),
        Q('Что выведет программа?', ['0 6', '6 0', '0 0', '3 6'], 0,
          'Метод с `params` принимает любое число аргументов, в том числе ноль.',
          code='class P\n{\n    static int Sum(params int[] nums)\n    {\n        int total = 0;\n        foreach (int n in nums) total += n;\n        return total;\n    }\n    static void Main()\n    {\n        Console.WriteLine(Sum() + " " + Sum(1, 2, 3));\n    }\n}'),
        Q('Что выведет программа?', ['True 3', 'False 0', 'True 7', 'False 3'], 0,
          '`out`-параметр получает значение внутри метода.',
          code='class P\n{\n    static bool TryDivide(int a, int b, out int result)\n    {\n        if (b == 0) { result = 0; return false; }\n        result = a / b;\n        return true;\n    }\n    static void Main()\n    {\n        bool ok = TryDivide(7, 2, out int q);\n        Console.WriteLine(ok + " " + q);\n    }\n}'),
        Q('Что выведет программа?', ['24', '10', '16', '4'], 0,
          '`4 * 3 * 2 * 1`.',
          code='class P\n{\n    static int Fact(int n) => n <= 1 ? 1 : n * Fact(n - 1);\n    static void Main()\n    {\n        Console.WriteLine(Fact(4));\n    }\n}'),
    ],
    videos=[],
    practice=r"""Разбивайте решение на небольшие методы. Для нескольких результатов используйте кортежи.""",
    problems=[('000069', 'НОД: алгоритм Евклида, можно рекурсией.'),
              ('000070', 'НОК через НОД.'),
              ('000683', 'Обратное число.'),
              ('000682', 'Перевод в двоичную систему.')],
    task=('Набор методов', r"""Напишите методы `IsPrime`, `DigitsSum`, `Fib` (рекурсивно и в цикле), `WordCount`, `Stats` (минимум, максимум и среднее кортежем). Покажите работу каждого на нескольких примерах и используйте `out` в одном из них.

Пришлите код и вывод."""),
    short='методы'))
