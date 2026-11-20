# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Массивы и ArrayList', pair(
    'Массивы и ArrayList',
    r"""### Массив

Массив хранит фиксированное число элементов одного типа. Длина задаётся при создании и не меняется.

```java
int[] a = new int[5];              // пять нулей
int[] b = {10, 20, 30};            // сразу со значениями
System.out.println(b.length);      // 3 (поле, а не метод)
b[0] = 99;
```

Элементы нумеруются с нуля. Выход за границы вызывает `ArrayIndexOutOfBoundsException`: в отличие от C++, Java проверяет индексы. Массив — ссылочный тип: `int[] c = b;` не копирует данные, обе переменные указывают на один массив.

Чтение массива:

```java
int n = sc.nextInt();
int[] a = new int[n];
for (int i = 0; i < n; i++) a[i] = sc.nextInt();
```

### Класс Arrays

```java
Arrays.sort(a);                       // сортировка
System.out.println(Arrays.toString(a)); // [10, 20, 30]
int[] copy = Arrays.copyOf(a, a.length);
Arrays.fill(a, 7);
boolean same = Arrays.equals(a, copy);
int pos = Arrays.binarySearch(a, 20);  // массив должен быть отсортирован
```

Сортировка массива чисел примитивных типов быстрая, но на некоторых специально подобранных тестах может деградировать. В олимпиадах иногда используют `Integer[]` или перемешивают массив перед сортировкой.

### Двумерные массивы

```java
int[][] grid = new int[3][4];
grid[1][2] = 5;
for (int[] row : grid) System.out.println(Arrays.toString(row));
```

### ArrayList

Массив не умеет расти. Если число элементов заранее неизвестно, используют `ArrayList`:

```java
ArrayList<Integer> list = new ArrayList<>();
list.add(10);
list.add(20);
list.add(0, 5);                  // вставить на позицию
System.out.println(list);          // [5, 10, 20]
System.out.println(list.get(1));   // 10
list.set(1, 99);
list.remove(0);                    // по индексу
System.out.println(list.size());
System.out.println(list.contains(99));
Collections.sort(list);
```

Хранить в `ArrayList` можно только объекты, поэтому используют обёртки: `Integer`, а не `int`. Преобразование выполняется автоматически.

### Перебор

```java
for (int x : list) System.out.print(x + " ");
for (int i = 0; i < list.size(); i++) System.out.print(list.get(i) + " ");
```

### Нюанс remove

У `ArrayList<Integer>` два метода: `remove(int index)` удаляет по индексу, `remove(Object o)` — по значению. Чтобы удалить число 5 (а не элемент с индексом 5), пишите `list.remove(Integer.valueOf(5))`.

### List.of и Arrays.asList

`List.of(1, 2, 3)` создаёт неизменяемый список: `add` вызовет исключение. `new ArrayList<>(List.of(1, 2, 3))` создаёт изменяемую копию.

### Что выбрать

| нужно | брать |
|---|---|
| фиксированное число элементов, максимум скорости | массив |
| число элементов меняется | `ArrayList` |
| нужны вставки и удаления в начале | `ArrayDeque` или `LinkedList` |
""",
    r"""- **Выход за границы.** `ArrayIndexOutOfBoundsException`. Последний индекс равен `length - 1`.
- **Присваивание массива.** `b = a` не копирует. Копируйте через `Arrays.copyOf` или `clone()`.
- **`remove(5)` в `ArrayList<Integer>`.** Удаляет элемент с индексом 5, а не число 5.
- **Изменение списка в `for-each`.** Приводит к `ConcurrentModificationException`.
- **`length` и `size()`.** Для массива `length` (без скобок), для списка `size()`, для строки `length()`.
- **Печать массива.** `System.out.println(arr)` выводит ссылку вида `[I@1b6d3586`. Используйте `Arrays.toString`.
- **Неизменяемый список.** `List.of(...)` не позволяет добавлять и удалять.
""",
    [
        Q('Что выведет программа?', ['[10, 20, 30]', '[I@15db9742', '10 20 30', '[10 20 30]'], 0,
          '`Arrays.toString` печатает содержимое массива.',
          code='int[] a = {10, 20, 30};\nSystem.out.println(Arrays.toString(a));'),
        Q('Что выведет программа?', ['99 99', '1 99', '99 1', '1 1'], 0,
          'Переменные `a` и `b` указывают на один и тот же массив.',
          code='int[] a = {1, 2};\nint[] b = a;\nb[0] = 99;\nSystem.out.println(a[0] + " " + b[0]);'),
        Q('Что выведет программа?', ['[1, 3, 4]', '[1, 2, 3]', '[2, 3, 4]', '[1, 2, 4]'], 0,
          '`remove(1)` для `ArrayList<Integer>` удаляет элемент по индексу 1, то есть число 2.',
          code='ArrayList<Integer> list = new ArrayList<>(List.of(1, 2, 3, 4));\nlist.remove(1);\nSystem.out.println(list);'),
        Q('Что выведет программа?', ['[1, 2, 4]', '[1, 3, 4]', '[2, 3, 4]', '[1, 2, 3]'], 0,
          '`Integer.valueOf(3)` превращает значение в объект, и вызывается `remove(Object)`: удаляется число 3.',
          code='ArrayList<Integer> list = new ArrayList<>(List.of(1, 2, 3, 4));\nlist.remove(Integer.valueOf(3));\nSystem.out.println(list);'),
        Q('Что выведет программа?', ['[1, 2, 3]', '[3, 2, 1]', '[2, 1, 3]', '[1, 3, 2]'], 0,
          '`Collections.sort` упорядочивает список по возрастанию.',
          code='ArrayList<Integer> list = new ArrayList<>(List.of(3, 1, 2));\nCollections.sort(list);\nSystem.out.println(list);'),
        Q('Что произойдёт во время выполнения?', ['UnsupportedOperationException: список неизменяемый', 'Выведет [1, 2, 3, 4]', 'Выведет [1, 2, 3]', 'Ошибка компиляции'], 0,
          '`List.of` возвращает неизменяемый список: добавлять и удалять элементы нельзя.',
          code='List<Integer> list = List.of(1, 2, 3);\nlist.add(4);\nSystem.out.println(list);'),
    ],
    videos=[('XD8azAEOu9U', 'Видео: ArrayList и LinkedList', 'Подробный урок об `ArrayList` и `LinkedList`: методы и различия.')],
    practice=r"""Массив читается так: сначала `n`, затем цикл с `nextInt`. Для сортировки используйте `Arrays.sort`.""",
    problems=[('000199', 'Сумма массива.'),
              ('000200', 'Максимум массива.'),
              ('000206', 'Развернуть массив.'),
              ('000202', 'Среднее арифметическое: приведение к `double`.')],
    task=('Список покупок', r"""Консольная программа с меню: добавить товар, удалить товар по номеру, показать список с номерами по алфавиту, выйти. Хранить товары в `ArrayList<String>`. Обработайте неверный номер и пустой список.

Пришлите код и пример сеанса."""),
    short='массивы'))
