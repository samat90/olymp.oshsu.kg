# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Исключения', pair(
    'Исключения: try, catch, finally, throw',
    r"""**Исключение** — объект, описывающий ошибку времени выполнения. Если его не обработать, программа завершится с сообщением и трассировкой стека.

```csharp
int[] a = new int[3];
Console.WriteLine(a[5]);    // IndexOutOfRangeException
```

### try / catch / finally

```csharp
try
{
    int n = int.Parse("12a");
    Console.WriteLine(n);
}
catch (FormatException e)
{
    Console.WriteLine("не число: " + e.Message);
}
finally
{
    Console.WriteLine("выполнится всегда");
}
```

- в блок `try` помещают код, который может вызвать ошибку;
- `catch` перехватывает исключение указанного типа; блоков `catch` может быть несколько, срабатывает первый подходящий (порядок: от частных к общим);
- `finally` выполняется всегда: после успешного завершения, после обработанной ошибки и даже при `return`.

### Часто встречающиеся исключения

| исключение | когда возникает |
|---|---|
| `FormatException` | неверный формат при разборе строки |
| `NullReferenceException` | обращение к `null` |
| `IndexOutOfRangeException` | индекс массива за границей |
| `ArgumentOutOfRangeException` | индекс списка за границей |
| `KeyNotFoundException` | нет ключа в словаре |
| `DivideByZeroException` | деление целых на ноль |
| `InvalidCastException` | неверное приведение типа |
| `InvalidOperationException` | операция недопустима в текущем состоянии |
| `ArgumentException`, `ArgumentNullException` | неверный аргумент метода |
| `OverflowException` | переполнение в `checked`-блоке |

Все они — наследники `System.Exception`. Свойства `Message` (текст) и `StackTrace` (цепочка вызовов) помогают найти причину.

### throw

```csharp
static void SetAge(int age)
{
    if (age < 0)
        throw new ArgumentException("возраст не может быть отрицательным");
}
```

Чтобы пробросить пойманное исключение дальше без потери трассировки, пишут просто `throw;` (а не `throw e;`).

### Фильтры исключений

```csharp
catch (Exception e) when (e.Message.Contains("файл"))
{
    ...
}
```

### Свои исключения

```csharp
class NoFuelException : Exception
{
    public NoFuelException(string message) : base(message) { }
}
```

### using и IDisposable

Объекты, владеющие ресурсами (файлы, соединения), закрывают через `using`:

```csharp
using (var reader = new StreamReader("diary.txt"))
{
    Console.WriteLine(reader.ReadLine());
}
```

Закрытие произойдёт автоматически, даже если случится исключение. Объект должен реализовать `IDisposable`.

### Правила хорошего тона

- ловите конкретные исключения, а не общий `Exception`;
- не оставляйте пустой `catch`: ошибка пропадёт бесследно;
- для ожидаемых ситуаций (проверка ввода) используйте `TryParse`, а не исключения: это быстрее и понятнее;
- исключения — для исключительных ситуаций, а не для обычного управления потоком.
""",
    r"""- **Пустой `catch`.** Ошибка исчезает, программа ведёт себя странно. Хотя бы запишите сообщение.
- **`catch (Exception)` везде.** Скрывает баги.
- **Порядок `catch`.** Общий тип перед частным вызовет ошибку компиляции.
- **`throw e;` вместо `throw;`.** Сбрасывает трассировку стека.
- **Деление на ноль.** Для целых — исключение, для `double` — `Infinity`.
- **`finally` и `return`.** Код в `finally` выполнится даже после `return`.
- **Исключения для обычной логики.** Они медленные; для проверки ввода используйте `TryParse`.
""",
    [
        Q('Что выведет программа?', ['не число\nконец', 'не число', '12\nконец', 'конец'], 0,
          'Исключение перехвачено, затем выполнился блок `finally`.',
          code='try\n{\n    int.Parse("12a");\n    Console.WriteLine("ok");\n}\ncatch (FormatException)\n{\n    Console.WriteLine("не число");\n}\nfinally\n{\n    Console.WriteLine("конец");\n}'),
        Q('Что выведет программа?', ['A', 'B', 'A B', 'Ошибка выполнения'], 0,
          'Срабатывает первый подходящий `catch`: `DivideByZeroException` перехватывается частным блоком.',
          code='try\n{\n    int a = 0;\n    Console.WriteLine(10 / a);\n}\ncatch (DivideByZeroException)\n{\n    Console.WriteLine("A");\n}\ncatch (Exception)\n{\n    Console.WriteLine("B");\n}'),
        Q('Что выведет программа?', ['finally\ntry', 'try\nfinally', 'try', 'finally'], 0,
          'Блок `finally` выполняется до того, как значение вернётся вызывающему.',
          code='class P\n{\n    static string F()\n    {\n        try { return "try"; }\n        finally { Console.WriteLine("finally"); }\n    }\n    static void Main()\n    {\n        Console.WriteLine(F());\n    }\n}'),
        Q('Что выведет программа?', ['Infinity', '0', 'Исключение', 'Ошибка компиляции'], 0,
          'Деление `double` на ноль исключения не вызывает.',
          code='double a = 1.0;\nConsole.WriteLine(a / 0);'),
        Q('Что выведет программа?', ['возраст не может быть отрицательным', 'ArgumentException', 'null', 'Ошибка компиляции'], 0,
          '`Message` возвращает текст, переданный в конструктор исключения.',
          code='try\n{\n    throw new ArgumentException("возраст не может быть отрицательным");\n}\ncatch (ArgumentException e)\n{\n    Console.WriteLine(e.Message);\n}'),
        Q('Что выведет программа?', ['ловим: Исходная ошибка', 'Исходная ошибка', 'ловим', 'Ошибка компиляции'], 0,
          '`throw;` пробрасывает исключение дальше без потери трассировки; внешний `catch` получает то же исключение.',
          code='try\n{\n    try { throw new Exception("Исходная ошибка"); }\n    catch { throw; }\n}\ncatch (Exception e)\n{\n    Console.WriteLine("ловим: " + e.Message);\n}'),
    ],
    videos=[],
    practice=r"""Читайте входные данные надёжно: используйте `TryParse` вместо `Parse`, где ввод может быть неверным.""",
    problems=[('000205', 'Второй максимум: подумайте, что делать, если все числа одинаковые.')],
    task=('Безопасный калькулятор', r"""Калькулятор читает числа и операцию. Неверное число — просит повторить (`TryParse`), деление на ноль — понятное сообщение, неизвестная операция — собственное исключение `BadOperationException`, которое перехватывается в `Main`. Используйте `try-catch-finally`.

Пришлите код и примеры «плохого» ввода."""),
    short='исключения'))
