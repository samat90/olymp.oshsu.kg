# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Коллекции: HashMap, HashSet и другие', pair(
    'Карты, множества и очереди',
    r"""Помимо списков, в Java Collections Framework есть контейнеры для других задач.

### HashMap: пары «ключ → значение»

```java
HashMap<String, Integer> prices = new HashMap<>();
prices.put("курут", 120);
prices.put("кымыз", 90);
prices.put("курут", 130);            // заменит значение
System.out.println(prices.get("курут"));   // 130
System.out.println(prices.get("мёд"));     // null
System.out.println(prices.getOrDefault("мёд", 0)); // 0
System.out.println(prices.containsKey("кымыз"));   // true
prices.remove("кымыз");
System.out.println(prices.size());
```

Обход:

```java
for (Map.Entry<String, Integer> e : prices.entrySet()) {
    System.out.println(e.getKey() + " = " + e.getValue());
}
for (String key : prices.keySet()) { ... }
for (int v : prices.values()) { ... }
```

Порядок обхода `HashMap` не определён. Если нужен порядок добавления, используют `LinkedHashMap`, если порядок по ключу — `TreeMap`.

Частый приём — подсчёт:

```java
Map<Character, Integer> count = new HashMap<>();
for (char c : "мама".toCharArray()) {
    count.put(c, count.getOrDefault(c, 0) + 1);
}
// или короче:
count.merge(c, 1, Integer::sum);
```

### HashSet: уникальные значения

```java
Set<Integer> seen = new HashSet<>();
seen.add(1);
seen.add(2);
seen.add(2);
System.out.println(seen.size());     // 2
System.out.println(seen.contains(2));  // true
```

`add` возвращает `false`, если элемент уже был. `TreeSet` хранит элементы отсортированными и умеет `first()`, `last()`, `ceiling(x)`, `floor(x)`.

### TreeMap

Карта, упорядоченная по ключу. Операции за логарифмическое время. Есть `firstKey()`, `lastKey()`, `floorKey(k)`, `ceilingKey(k)`.

### Очереди и стеки

```java
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1);
stack.push(2);
System.out.println(stack.pop());   // 2: последний пришёл, первый ушёл

Queue<Integer> queue = new ArrayDeque<>();
queue.add(1);
queue.add(2);
System.out.println(queue.poll());  // 1: первый пришёл, первый ушёл
```

Для стека и очереди берите `ArrayDeque`, а не `Stack` и `LinkedList`: он быстрее.

`PriorityQueue` всегда отдаёт наименьший элемент:

```java
PriorityQueue<Integer> pq = new PriorityQueue<>();
pq.add(5); pq.add(1); pq.add(3);
System.out.println(pq.poll());   // 1
```

### Интерфейсы и реализации

Принято объявлять переменную по интерфейсу, а создавать конкретный класс: `List<Integer> list = new ArrayList<>();`, `Map<String, Integer> m = new HashMap<>();`. Тогда реализацию легко заменить.

### Что выбрать

| нужно | брать |
|---|---|
| поиск по ключу, порядок неважен | `HashMap` |
| поиск по ключу, порядок по ключу | `TreeMap` |
| уникальные значения | `HashSet`, `TreeSet` |
| стек, очередь | `ArrayDeque` |
| всегда наименьший элемент | `PriorityQueue` |
""",
    r"""- **`null` вместо значения.** `map.get(k)` для отсутствующего ключа возвращает `null`. Присвоение `int x = map.get(k)` бросит `NullPointerException`. Используйте `getOrDefault`.
- **Ключи-массивы.** `int[]` в качестве ключа сравнивается по ссылке. Используйте `List<Integer>` или строку.
- **Изменяемые ключи.** Если ключ изменили после добавления, его не найти.
- **Порядок в `HashMap`.** Не рассчитывайте на него.
- **Удаление во время обхода.** Используйте итератор или `removeIf`.
- **`Stack` и `LinkedList` для очереди.** Работают, но медленнее `ArrayDeque`.
- **`PriorityQueue` и обход.** Итерация по ней не даёт отсортированного порядка; порядок гарантирует только `poll`.
""",
    [
        Q('Что выведет программа?', ['3 10', '3 1', '2 10', '4 10'], 0,
          'Ключ `"c"` добавлен, значение `"a"` заменено.',
          code='Map<String, Integer> d = new HashMap<>();\nd.put("a", 1);\nd.put("b", 2);\nd.put("c", 3);\nd.put("a", 10);\nSystem.out.println(d.size() + " " + d.get("a"));'),
        Q('Что выведет программа?', ['null 0', '0 0', 'null null', 'Ошибка выполнения'], 0,
          'Для отсутствующего ключа `get` возвращает `null`, а `getOrDefault` — запасное значение.',
          code='Map<String, Integer> m = new HashMap<>();\nSystem.out.println(m.get("x") + " " + m.getOrDefault("x", 0));'),
        Q('Что выведет программа?', ['3', '6', '2', '1'], 0,
          'Множество хранит только уникальные значения.',
          code='Set<Integer> s = new HashSet<>(List.of(1, 2, 2, 3, 3, 3));\nSystem.out.println(s.size());'),
        Q('Что выведет программа?', ['[1, 2, 3, 5]', '[5, 1, 3, 2]', '[1, 2, 5, 3]', '[5, 3, 2, 1]'], 0,
          '`TreeSet` хранит элементы по возрастанию.',
          code='Set<Integer> s = new TreeSet<>(List.of(5, 1, 3, 2));\nSystem.out.println(s);'),
        Q('Что выведет программа?', ['2 1', '1 2', '2 2', '1 1'], 0,
          'Стек выдаёт последний добавленный элемент, очередь — первый.',
          code='Deque<Integer> stack = new ArrayDeque<>();\nstack.push(1);\nstack.push(2);\nQueue<Integer> q = new ArrayDeque<>();\nq.add(1);\nq.add(2);\nSystem.out.println(stack.pop() + " " + q.poll());'),
        Q('Что выведет программа?', ['1 3 5 ', '5 3 1 ', '3 1 5 ', '1 5 3 '], 0,
          '`PriorityQueue` всегда отдаёт наименьший элемент.',
          code='PriorityQueue<Integer> pq = new PriorityQueue<>();\npq.add(5);\npq.add(1);\npq.add(3);\nwhile (!pq.isEmpty()) System.out.print(pq.poll() + " ");'),
    ],
    videos=[('Ka3_4vxMGjM', 'Видео: коллекция HashMap', 'Первая часть разбора `HashMap`: основные приёмы работы.')],
    practice=r"""Подсчёт частот и поиск уникальных значений — задачи для `HashMap` и `HashSet`.""",
    problems=[('000208', 'Сколько разных чисел в массиве.'),
              ('000105', 'Самый частый символ.'),
              ('000306', 'Мода массива.'),
              ('000106', 'Удалить дубликаты, сохранив порядок: `LinkedHashSet`.')],
    task=('Частоты слов', r"""Прочитайте текст до конца ввода, подсчитайте слова без учёта регистра и выведите их по убыванию частоты, а при равенстве по алфавиту. Используйте `HashMap`, затем список записей с компаратором.

Пришлите код и пример."""),
    short='коллекции'))
