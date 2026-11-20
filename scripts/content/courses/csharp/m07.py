# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Dictionary, HashSet, Queue, Stack', pair(
    'Словари, множества, очереди и стеки',
    r"""Помимо `List<T>`, в `System.Collections.Generic` есть контейнеры для других задач.

### Dictionary

Словарь хранит пары «ключ → значение» и ищет по ключу за постоянное время.

```csharp
var prices = new Dictionary<string, int>();
prices["курут"] = 120;
prices["кымыз"] = 90;
prices["курут"] = 130;                 // заменит значение
Console.WriteLine(prices["курут"]);    // 130
Console.WriteLine(prices.Count);       // 2
Console.WriteLine(prices.ContainsKey("мёд"));   // False
prices.Remove("кымыз");
```

Обращение к отсутствующему ключу бросает `KeyNotFoundException`. Безопасное чтение:

```csharp
if (prices.TryGetValue("мёд", out int price))
    Console.WriteLine(price);
else
    Console.WriteLine("нет в продаже");
```

Обход:

```csharp
foreach (KeyValuePair<string, int> pair in prices)
    Console.WriteLine(pair.Key + " = " + pair.Value);
foreach (var key in prices.Keys) { ... }
foreach (var v in prices.Values) { ... }
```

Порядок элементов не гарантируется. Если нужен порядок по ключу, берут `SortedDictionary`.

Подсчёт частот:

```csharp
var count = new Dictionary<char, int>();
foreach (char c in "мама")
{
    if (!count.ContainsKey(c)) count[c] = 0;
    count[c]++;
}
```

### HashSet

Множество уникальных значений. `Add` возвращает `false`, если элемент уже есть.

```csharp
var seen = new HashSet<int>();
seen.Add(1);
seen.Add(2);
Console.WriteLine(seen.Add(2));      // False
Console.WriteLine(seen.Count);       // 2
Console.WriteLine(seen.Contains(1)); // True
```

Есть операции над множествами: `UnionWith`, `IntersectWith`, `ExceptWith`. `SortedSet<T>` хранит значения по порядку.

### Queue и Stack

```csharp
var queue = new Queue<int>();
queue.Enqueue(1);
queue.Enqueue(2);
Console.WriteLine(queue.Dequeue());   // 1: первый пришёл, первый ушёл

var stack = new Stack<int>();
stack.Push(1);
stack.Push(2);
Console.WriteLine(stack.Pop());       // 2: последний пришёл, первый ушёл
```

`Peek()` смотрит на следующий элемент, не извлекая его. Вызов `Dequeue()` или `Pop()` для пустого контейнера бросает исключение: проверяйте `Count`.

### Другие контейнеры

- `LinkedList<T>` — двусвязный список;
- `PriorityQueue<TElement, TPriority>` (в новых версиях .NET) — очередь с приоритетом;
- `SortedDictionary`, `SortedList` — упорядоченные словари.

### Что выбрать

| нужно | брать |
|---|---|
| поиск по ключу | `Dictionary` |
| уникальные значения, быстрая проверка наличия | `HashSet` |
| «первым пришёл, первым вышел» | `Queue` |
| «последним пришёл, первым вышел» | `Stack` |
| упорядоченные по ключу данные | `SortedDictionary`, `SortedSet` |
""",
    r"""- **`KeyNotFoundException`.** Чтение `d[k]` для отсутствующего ключа. Используйте `TryGetValue` или `ContainsKey`.
- **Двойной поиск.** `if (d.ContainsKey(k)) x = d[k];` ищет ключ два раза. `TryGetValue` ищет один.
- **Изменяемые ключи.** Если ключ изменили после добавления, его не найти.
- **Порядок в `Dictionary` и `HashSet`.** Не гарантирован.
- **Изменение коллекции в `foreach`.** `InvalidOperationException`.
- **`Dequeue` и `Pop` из пустого контейнера.** Исключение; сначала проверяйте `Count`.
- **Ключ-массив.** Сравнивается по ссылке. Берите строку или кортеж.
""",
    [
        Q('Что выведет программа?', ['3 10', '3 1', '2 10', '4 10'], 0,
          'Ключ `"c"` добавлен, значение `"a"` заменено.',
          code='var d = new Dictionary<string, int>();\nd["a"] = 1;\nd["b"] = 2;\nd["c"] = 3;\nd["a"] = 10;\nConsole.WriteLine(d.Count + " " + d["a"]);'),
        Q('Что выведет программа?', ['False 0', 'True 5', 'False 5', 'Исключение'], 0,
          '`TryGetValue` не бросает исключение: для отсутствующего ключа вернёт `false` и значение по умолчанию.',
          code='var d = new Dictionary<string, int>();\nd["x"] = 5;\nint v;\nbool ok = d.TryGetValue("y", out v);\nConsole.WriteLine(ok + " " + v);'),
        Q('Что выведет программа?', ['3', '6', '2', '1'], 0,
          'Множество хранит только уникальные значения.',
          code='var s = new HashSet<int> { 1, 2, 2, 3, 3, 3 };\nConsole.WriteLine(s.Count);'),
        Q('Что выведет программа?', ['False', 'True', '2', '1'], 0,
          '`Add` возвращает `false`, если элемент уже был в множестве.',
          code='var s = new HashSet<int>();\ns.Add(1);\nConsole.WriteLine(s.Add(1));'),
        Q('Что выведет программа?', ['2 1', '1 2', '2 2', '1 1'], 0,
          'Стек выдаёт последний добавленный элемент, очередь — первый.',
          code='var st = new Stack<int>();\nst.Push(1); st.Push(2);\nvar q = new Queue<int>();\nq.Enqueue(1); q.Enqueue(2);\nConsole.WriteLine(st.Pop() + " " + q.Dequeue());'),
        Q('Что произойдёт?', ['Исключение KeyNotFoundException', 'Выведет 0', 'Выведет null', 'Ошибка компиляции'], 0,
          'Чтение несуществующего ключа через индексатор бросает исключение.',
          code='var d = new Dictionary<string, int>();\nConsole.WriteLine(d["нет"]);'),
    ],
    videos=[],
    practice=r"""Подсчёт частот и уникальных значений — задачи для `Dictionary` и `HashSet`.""",
    problems=[('000208', 'Сколько разных чисел в массиве.'),
              ('000105', 'Самый частый символ.'),
              ('000306', 'Мода массива.'),
              ('000106', 'Удалить дубликаты, сохранив порядок: множество «уже видели».')],
    task=('Частоты слов', r"""Прочитайте текст до конца ввода, подсчитайте слова без учёта регистра и выведите их по убыванию частоты, а при равенстве по алфавиту. Используйте `Dictionary` и сортировку списка пар.

Пришлите код и пример."""),
    short='коллекции'))
