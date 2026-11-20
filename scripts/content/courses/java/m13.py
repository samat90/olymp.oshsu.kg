# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Stream API', pair(
    'Stream API и Optional',
    r"""**Stream** — конвейер для обработки данных: берём источник (список, массив), выполняем цепочку преобразований и получаем результат. Исходная коллекция не меняется.

```java
List<Integer> nums = List.of(5, 2, 8, 1, 9, 4);

List<Integer> result = nums.stream()
    .filter(n -> n % 2 == 0)      // оставить чётные
    .map(n -> n * n)               // возвести в квадрат
    .sorted()                      // по возрастанию
    .collect(Collectors.toList()); // собрать в список

System.out.println(result);        // [16, 64, 4] после сортировки: [4, 16, 64]
```

Цепочка состоит из трёх частей:

1. **источник**: `list.stream()`, `Arrays.stream(array)`, `Stream.of(1, 2, 3)`, `IntStream.range(0, 5)`;
2. **промежуточные операции** (возвращают новый поток): `filter`, `map`, `sorted`, `distinct`, `limit`, `skip`, `flatMap`;
3. **терминальная операция** (запускает вычисление и завершает поток): `collect`, `forEach`, `count`, `sum`, `min`, `max`, `reduce`, `anyMatch`, `allMatch`, `findFirst`.

Пока нет терминальной операции, ничего не вычисляется (ленивые вычисления). После терминальной операции поток использовать повторно нельзя.

### Основные приёмы

```java
long count = nums.stream().filter(n -> n > 3).count();
int sum = nums.stream().mapToInt(Integer::intValue).sum();
OptionalInt max = nums.stream().mapToInt(n -> n).max();
boolean anyBig = nums.stream().anyMatch(n -> n > 8);
String joined = names.stream().collect(Collectors.joining(", "));
```

Для чисел есть специализированные потоки `IntStream`, `LongStream`, `DoubleStream` с методами `sum`, `average`, `max`, `min` без упаковки значений.

```java
int total = IntStream.rangeClosed(1, 100).sum();   // 5050
```

### Сбор результатов

```java
// список слов длиннее трёх букв в верхнем регистре
List<String> r = words.stream()
    .filter(w -> w.length() > 3)
    .map(String::toUpperCase)
    .toList();                                      // Java 16+

// группировка по длине
Map<Integer, List<String>> byLength = words.stream()
    .collect(Collectors.groupingBy(String::length));

// подсчёт
Map<String, Long> counts = words.stream()
    .collect(Collectors.groupingBy(w -> w, Collectors.counting()));
```

### reduce

Свёртка потока к одному значению:

```java
int product = Stream.of(1, 2, 3, 4).reduce(1, (a, b) -> a * b);  // 24
```

### Optional

Результат, которого может не быть (например, `findFirst`, `max`), оборачивается в `Optional`:

```java
Optional<String> first = names.stream().filter(n -> n.startsWith("Н")).findFirst();
System.out.println(first.orElse("не найдено"));
first.ifPresent(System.out::println);
```

`Optional` заставляет явно обработать отсутствие значения вместо `null`.

### Когда не нужен Stream

Для простых циклов обычный `for` часто понятнее и быстрее. Потоки хороши, когда нужно описать цепочку «отфильтровать, преобразовать, собрать». В олимпиадных задачах с жёсткими лимитами времени потоки используют осторожно: они медленнее циклов.
""",
    r"""- **Нет терминальной операции.** `list.stream().map(...)` без `collect` и подобных ничего не делает.
- **Повторное использование потока.** После терминальной операции поток закрыт: `IllegalStateException`.
- **Изменение внешней переменной в лямбде.** Нельзя (эффективно финальные), а потоки не для побочных эффектов.
- **`Collectors.toList()` и неизменяемость.** `toList()` из Java 16 возвращает неизменяемый список.
- **`get()` у пустого `Optional`.** `NoSuchElementException`. Используйте `orElse`, `ifPresent`.
- **Боксинг.** `Stream<Integer>` медленнее `IntStream`; для сумм и максимумов берите `mapToInt`.
- **Сортировка по составному ключу.** Используйте `Comparator.comparing(...).thenComparing(...)`.
""",
    [
        Q('Что выведет программа?', ['[4, 16, 64]', '[16, 64, 4]', '[2, 8, 4]', '[4, 64, 16]'], 0,
          'Чётные числа 2, 8, 4 возводятся в квадрат и сортируются.',
          code='List<Integer> r = Stream.of(5, 2, 8, 1, 9, 4)\n    .filter(n -> n % 2 == 0)\n    .map(n -> n * n)\n    .sorted()\n    .collect(Collectors.toList());\nSystem.out.println(r);'),
        Q('Что выведет программа?', ['5050', '5000', '100', '5051'], 0,
          '`rangeClosed(1, 100)` включает обе границы.',
          code='System.out.println(IntStream.rangeClosed(1, 100).sum());'),
        Q('Что выведет программа?', ['3', '6', '2', '1'], 0,
          'Условию `n > 3` удовлетворяют 5, 8, 9 — три числа.',
          code='long c = Stream.of(5, 2, 8, 1, 9, 4).filter(n -> n > 4).count();\nSystem.out.println(c);'),
        Q('Что выведет программа?', ['24', '10', '9', '1'], 0,
          '`reduce` последовательно умножает элементы, начиная с единицы.',
          code='System.out.println(Stream.of(1, 2, 3, 4).reduce(1, (a, b) -> a * b));'),
        Q('Что выведет программа?', ['не найдено', 'null', 'NoSuchElementException', 'Ошибка компиляции'], 0,
          'Подходящего элемента нет, `Optional` пуст, `orElse` возвращает запасное значение.',
          code='Optional<String> first = Stream.of("Ош", "Нарын").filter(n -> n.startsWith("Б")).findFirst();\nSystem.out.println(first.orElse("не найдено"));'),
        Q('Что выведет программа?', ['a-b-c', 'abc', '[a, b, c]', 'a b c'], 0,
          '`Collectors.joining` склеивает строки потока через разделитель.',
          code='System.out.println(Stream.of("a", "b", "c").collect(Collectors.joining("-")));'),
    ],
    videos=[('aC0-KsuPG0I', 'Видео: основы Stream API', 'Практическое введение в Stream API.'),
            ('Z39TdDOnJVU', 'Видео: терминальные и промежуточные операции', 'Разбор промежуточных и терминальных операций потока.')],
    practice=r"""Поток подходит для кратких преобразований. Попробуйте решить задачи двумя способами: циклом и потоком, сравните читаемость.""",
    problems=[('000204', 'Количество чётных: `filter` и `count`.'),
              ('000203', 'Количество положительных.'),
              ('000207', 'Префиксные суммы: потоком здесь неудобно, обычный цикл понятнее.')],
    task=('Анализ оценок', r"""Дан список студентов (имя, группа, балл). Используя только потоки, найдите: средний балл по каждой группе, лучшего студента в каждой группе, имена всех студентов с баллом выше среднего по всем, и выведите их через запятую в алфавитном порядке.

Пришлите код и вывод."""),
    short='Stream'))
