# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Строки', pair(
    'Строки: string и StringBuilder',
    r"""`string` — ссылочный тип, но ведёт себя как значение: строки **неизменяемы**. Любая операция создаёт новую строку, старая остаётся прежней.

```csharp
string city = "Каракол";
Console.WriteLine(city.Length);        // 7
Console.WriteLine(city[0]);            // К
Console.WriteLine(city.ToUpper());     // КАРАКОЛ
Console.WriteLine(city);               // Каракол (не изменилась)
```

Индексы начинаются с нуля. `Length` — свойство (без скобок). `city[i]` возвращает `char`; выход за границы вызывает `IndexOutOfRangeException`.

### Основные методы

| метод | что делает |
|---|---|
| `Substring(a, len)` | подстрока: начало и длина |
| `IndexOf(x)` | позиция первого вхождения или `-1` |
| `Contains(x)` | есть ли подстрока |
| `StartsWith(x)`, `EndsWith(x)` | начало и конец |
| `Replace(a, b)` | замена всех вхождений |
| `Trim()` | убрать пробелы по краям |
| `Split(' ')` | разбить на массив строк |
| `string.Join("-", массив)` | склеить |
| `ToUpper()`, `ToLower()` | регистр |
| `string.IsNullOrEmpty(s)` | пустая или `null` |
| `PadLeft(n)`, `PadRight(n)` | дополнить пробелами |

Внимание: `Substring` принимает **начало и длину**, а не начало и конец, как в Java.

### Сравнение

В C# оператор `==` для строк сравнивает **содержимое**, а не ссылки (в отличие от Java):

```csharp
string a = "привет";
string b = new string("привет".ToCharArray());
Console.WriteLine(a == b);        // True
Console.WriteLine(a.Equals(b));    // True
```

Для сравнения без учёта регистра: `string.Equals(a, b, StringComparison.OrdinalIgnoreCase)`. Для упорядочивания: `string.Compare(a, b)` и `a.CompareTo(b)`.

### Склейка и StringBuilder

Оператор `+` создаёт новую строку, в цикле это медленно. Для многократных дополнений используют `StringBuilder` (пространство имён `System.Text`):

```csharp
var sb = new StringBuilder();
for (int i = 0; i < 3; i++)
    sb.Append("ab");
Console.WriteLine(sb.ToString());   // ababab
```

### Символы

`char` — один символ. Методы: `char.IsDigit(c)`, `char.IsLetter(c)`, `char.IsUpper(c)`, `char.ToUpper(c)`. Код цифры в число: `c - '0'`.

### Интерполяция и формат

```csharp
Console.WriteLine($"{name}, {age} лет");
string s = string.Format("{0:F2}", 3.14159);
```

### Буквальные и многострочные строки

Строка с префиксом `@` не обрабатывает `\`: удобно для путей `@"C:\temp\file.txt"`. Она может занимать несколько строк.

### Преобразования

`Convert.ToString(5)`, `5.ToString()`, `int.Parse("42")`, `s.ToCharArray()` (строка в массив символов), `new string(chars)` (обратно).

### Обход

```csharp
foreach (char c in "Ош") Console.WriteLine(c);
```
""",
    r"""- **Строка не меняется.** `s.ToUpper();` без присваивания ничего не даёт.
- **`Substring(a, b)` как «с a до b».** На самом деле второй аргумент — длина.
- **Выход за границы** вызывает исключение: проверяйте `Length`.
- **Склейка в цикле через `+`.** Для больших объёмов используйте `StringBuilder`.
- **`null`-строка.** `s.Length` у `null` даёт `NullReferenceException`; `string.IsNullOrEmpty` проверяет оба случая.
- **Регистр при сравнении.** `"Ош" == "ош"` ложно.
- **Изменение символа по индексу.** `s[0] = 'X'` не компилируется: преобразуйте в массив `char[]`.
""",
    [
        Q('Что выведет программа?', ['7', '8', '6', '14'], 0,
          '`Length` возвращает число символов.',
          code='string s = "Каракол";\nConsole.WriteLine(s.Length);'),
        Q('Что выведет программа?', ['ell', 'ello', 'Hel', 'el'], 0,
          '`Substring(1, 3)`: начало 1, длина 3.',
          code='Console.WriteLine("Hello".Substring(1, 3));'),
        Q('Что выведет программа?', ['True True', 'False True', 'True False', 'False False'], 0,
          'В C# `==` для строк сравнивает содержимое.',
          code='string a = "привет";\nstring b = new string("привет".ToCharArray());\nConsole.WriteLine((a == b) + " " + a.Equals(b));'),
        Q('Что выведет программа?', ['abc', 'ABC', 'aBc', 'Abc'], 0,
          'Метод вернул новую строку, но результат не присвоен.',
          code='string s = "abc";\ns.ToUpper();\nConsole.WriteLine(s);'),
        Q('Что выведет программа?', ['3', '1', '0', '4'], 0,
          '`Split(\' \')` делит по пробелу, получаются три слова.',
          code='string[] words = "раз два три".Split(\' \');\nConsole.WriteLine(words.Length);'),
        Q('Что выведет программа?', ['a-b-c', 'a b c', 'abc', '[a, b, c]'], 0,
          '`string.Join` склеивает массив через разделитель.',
          code='Console.WriteLine(string.Join("-", "a b c".Split(\' \')));'),
        Q('Что выведет программа?', ['olleH', 'Hello', 'H', 'Ошибка компиляции'], 0,
          'Строку превращают в массив символов, разворачивают и собирают обратно.',
          code='char[] chars = "Hello".ToCharArray();\nArray.Reverse(chars);\nConsole.WriteLine(new string(chars));'),
    ],
    videos=[],
    practice=r"""Для чтения строки целиком используйте `Console.ReadLine`. Для длинных текстов результат собирайте в `StringBuilder`.""",
    problems=[('000099', 'Длина строки.'),
              ('000103', 'Верхний регистр.'),
              ('000100', 'Перевернуть строку: `Array.Reverse`.'),
              ('000107', 'Количество слов: `Split` с параметром, убирающим пустые элементы.')],
    task=('Анализ текста', r"""Прочитайте строку целиком. Выведите: длину, количество слов, строку задом наперёд, строку в верхнем регистре, количество каждой гласной. Затем проверьте, является ли строка палиндромом (без учёта регистра и пробелов).

Пришлите код и пример."""),
    short='строки'))
