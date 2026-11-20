# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Массивы и List<T>', pair(
    'Массивы и List',
    r"""### Массив

Массив хранит фиксированное число элементов одного типа.

```csharp
int[] a = new int[5];             // пять нулей
int[] b = { 10, 20, 30 };         // сразу со значениями
Console.WriteLine(b.Length);      // 3
b[0] = 99;
```

Индексы с нуля. Выход за границы вызывает `IndexOutOfRangeException`. Массив — ссылочный тип: `int[] c = b;` не копирует данные, обе переменные указывают на один массив.

Чтение массива чисел из одной строки:

```csharp
int[] a = Console.ReadLine().Split(' ').Select(int.Parse).ToArray();
```

(нужен `using System.Linq;`).

### Класс Array

```csharp
Array.Sort(a);                  // сортировка по возрастанию
Array.Reverse(a);               // разворот
int pos = Array.IndexOf(a, 20); // индекс или -1
Array.Resize(ref a, 10);        // изменить размер (создаёт новый массив)
int[] copy = (int[])a.Clone();
```

Вывод содержимого: `string.Join(" ", a)`.

### Многомерные и «рваные» массивы

```csharp
int[,] grid = new int[3, 4];    // прямоугольный
grid[1, 2] = 5;
int[][] jagged = new int[3][];  // массив массивов
jagged[0] = new int[] { 1, 2 };
```

### List<T>

`List<T>` — динамический массив: размер меняется. Находится в `System.Collections.Generic`.

```csharp
var list = new List<int>();
list.Add(10);
list.Add(20);
list.Insert(0, 5);                 // вставить на позицию
Console.WriteLine(list.Count);     // 3 (свойство Count)
Console.WriteLine(list[1]);        // 10
list[1] = 99;
list.Remove(99);                   // удалить по значению
list.RemoveAt(0);                  // удалить по индексу
Console.WriteLine(list.Contains(20));
list.Sort();
list.Reverse();
```

Список можно создать с начальными значениями: `new List<int> { 3, 1, 2 }`. Перебор: `foreach (int x in list)` или `for` по индексам. Удалять элементы внутри `foreach` нельзя; используйте `list.RemoveAll(x => x < 0)`.

### Полезные методы

```csharp
list.Max();   list.Min();   list.Sum();   list.Average();   // System.Linq
list.IndexOf(20);
list.ToArray();
list.AddRange(new[] { 7, 8 });
list.Clear();
```

### Нюанс сортировки

`Sort()` без аргументов сортирует по возрастанию. Для своего порядка передают сравнение:

```csharp
list.Sort((a, b) => b.CompareTo(a));    // по убыванию
```

### Что выбрать

| нужно | брать |
|---|---|
| фиксированный размер, максимум скорости | массив |
| размер меняется | `List<T>` |
| вставки и удаления с обоих концов | `LinkedList<T>`, `Queue<T>`, `Deque` |
""",
    r"""- **Выход за границы.** `IndexOutOfRangeException` для массива, `ArgumentOutOfRangeException` для списка.
- **Присваивание массива.** `b = a` не копирует данные.
- **`Length` и `Count`.** У массива `Length`, у списка `Count`, у строки `Length`.
- **`Remove` и `RemoveAt`.** Первый удаляет по значению, второй по индексу. Для `List<int>` легко перепутать.
- **Изменение списка в `foreach`.** `InvalidOperationException`: коллекция была изменена.
- **Печать массива.** `Console.WriteLine(arr)` выводит `System.Int32[]`. Используйте `string.Join`.
- **Забыли `using System.Linq`.** Методы `Max`, `Sum`, `Select` без него недоступны.
""",
    [
        Q('Что выведет программа?', ['10 20 30', 'System.Int32[]', '[10, 20, 30]', '102030'], 0,
          '`string.Join` собирает элементы массива в строку с разделителем.',
          code='int[] a = { 10, 20, 30 };\nConsole.WriteLine(string.Join(" ", a));'),
        Q('Что выведет программа?', ['99 99', '1 99', '99 1', '1 1'], 0,
          'Обе переменные указывают на один и тот же массив.',
          code='int[] a = { 1, 2 };\nint[] b = a;\nb[0] = 99;\nConsole.WriteLine(a[0] + " " + b[0]);'),
        Q('Что выведет программа?', ['3 20', '2 20', '3 10', '4 20'], 0,
          '`Count` — число элементов, `list[1]` — второй элемент.',
          code='var list = new List<int>();\nlist.Add(10);\nlist.Add(20);\nlist.Add(30);\nConsole.WriteLine(list.Count + " " + list[1]);'),
        Q('Что выведет программа?', ['1 3 4', '1 2 3 4', '2 3 4', '1 2 4'], 0,
          '`RemoveAt(1)` удаляет элемент по индексу 1, то есть число 2.',
          code='var list = new List<int> { 1, 2, 3, 4 };\nlist.RemoveAt(1);\nConsole.WriteLine(string.Join(" ", list));'),
        Q('Что выведет программа?', ['3 2 1', '1 2 3', '2 1 3', '3 1 2'], 0,
          'Сравнение `b.CompareTo(a)` даёт порядок по убыванию.',
          code='var list = new List<int> { 2, 3, 1 };\nlist.Sort((a, b) => b.CompareTo(a));\nConsole.WriteLine(string.Join(" ", list));'),
        Q('Что произойдёт?', ['Исключение: коллекция была изменена во время перебора', 'Выведет 1 3', 'Выведет 1 2 3', 'Ошибка компиляции'], 0,
          'Нельзя менять список, по которому идёт `foreach`.',
          code='var list = new List<int> { 1, 2, 3 };\nforeach (int x in list)\n    if (x == 2) list.Remove(x);'),
    ],
    videos=[],
    practice=r"""Массив читается так: сначала `n`, затем строка с числами; её удобно разобрать через `Split` и `Select(int.Parse)`.""",
    problems=[('000199', 'Сумма массива.'),
              ('000200', 'Максимум массива.'),
              ('000206', 'Развернуть массив.'),
              ('000202', 'Среднее арифметическое: приведение к `double`.')],
    task=('Список покупок', r"""Консольная программа с меню: добавить товар, удалить товар по номеру, показать список с номерами по алфавиту, выйти. Хранить товары в `List<string>`. Обработайте неверный номер и пустой список.

Пришлите код и пример сеанса."""),
    short='массивы'))
