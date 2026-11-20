# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Дженерики и лямбды', pair(
    'Дженерики, Comparable, Comparator, лямбды',
    r"""### Дженерики

Без дженериков коллекция хранит `Object`, и приходится приводить типы вручную. **Дженерики** (обобщения) позволяют указать, какой тип хранится:

```java
List<String> names = new ArrayList<>();
names.add("Нурзат");
String first = names.get(0);     // без приведения
// names.add(5);                 // ошибка компиляции
```

Ошибка типа обнаруживается при компиляции, а не при запуске.

### Свой обобщённый класс и метод

```java
class Box<T> {
    private T value;
    Box(T value) { this.value = value; }
    T get() { return value; }
}

Box<Integer> a = new Box<>(5);
Box<String> b = new Box<>("Ош");

static <T> void printAll(List<T> list) {
    for (T x : list) System.out.println(x);
}

static <T extends Comparable<T>> T biggest(T a, T b) {
    return a.compareTo(b) > 0 ? a : b;
}
```

`<T extends Comparable<T>>` — **ограничение**: подойдёт только тип, умеющий сравниваться. Вместо `T` нельзя подставлять примитивы: пишут `Integer`, а не `int`.

Подстановочный знак `?` обозначает «любой тип»: `List<?>`, `List<? extends Number>` (читать можно, добавлять нельзя).

### Сравнение объектов

Чтобы сортировать объекты, нужно задать порядок. Есть два способа.

**Comparable** — естественный порядок, заложенный в класс:

```java
class Student implements Comparable<Student> {
    String name; int score;
    Student(String name, int score) { this.name = name; this.score = score; }

    public int compareTo(Student o) {
        return Integer.compare(score, o.score);
    }
}
```

Метод возвращает отрицательное число, если «меньше», ноль для равных, положительное, если «больше». Теперь `Collections.sort(list)` работает для студентов.

**Comparator** — внешнее правило сравнения:

```java
list.sort(Comparator.comparing((Student s) -> s.name));
list.sort(Comparator.comparingInt((Student s) -> s.score).reversed());
list.sort(Comparator.comparingInt((Student s) -> s.score).thenComparing(s -> s.name));
```

### Лямбда-выражения

**Лямбда** — короткая запись функции: `(параметры) -> выражение`.

```java
Comparator<String> byLength = (a, b) -> a.length() - b.length();
Runnable r = () -> System.out.println("запуск");
```

Лямбду можно использовать там, где требуется **функциональный интерфейс** (с одним абстрактным методом). Стандартные:

| интерфейс | метод | пример |
|---|---|---|
| `Function<T, R>` | `R apply(T t)` | `s -> s.length()` |
| `Predicate<T>` | `boolean test(T t)` | `n -> n > 0` |
| `Consumer<T>` | `void accept(T t)` | `x -> System.out.println(x)` |
| `Supplier<T>` | `T get()` | `() -> 42` |
| `BiFunction<A, B, R>` | `R apply(A a, B b)` | `(a, b) -> a + b` |

```java
Predicate<Integer> isEven = n -> n % 2 == 0;
System.out.println(isEven.test(4));   // true
```

### Ссылки на методы

Если лямбда лишь вызывает существующий метод, её можно сократить: `String::length`, `System.out::println`, `Integer::compare`.

```java
names.forEach(System.out::println);
```

### Захват переменных

Лямбда может использовать локальные переменные внешнего метода, но только те, значение которых не меняется после присваивания (**эффективно финальные**).
""",
    r"""- **Примитив в дженерике.** `List<int>` не компилируется: используйте `List<Integer>`.
- **Сравнение через вычитание.** `a - b` в компараторе при больших числах переполняется. Пишите `Integer.compare(a, b)`.
- **`compareTo` не согласован с `equals`.** Возникают неожиданности в `TreeSet` и `TreeMap`.
- **Изменяемая переменная в лямбде.** Ошибка компиляции «должна быть финальной или эффективно финальной».
- **Стирание типов.** Во время выполнения `List<String>` и `List<Integer>` одинаковы: нельзя написать `new T()` или `instanceof List<String>`.
- **Сортировка массива объектов, не реализующих `Comparable`.** `ClassCastException`.
""",
    [
        Q('Что выведет программа?', ['5 Ош', 'Ош 5', '5', 'Ошибка компиляции'], 0,
          'Один и тот же обобщённый класс работает с разными типами значений.',
          code='public class Main {\n    static class Box<T> {\n        T value;\n        Box(T value) { this.value = value; }\n        T get() { return value; }\n    }\n\n    public static void main(String[] args) {\n        Box<Integer> a = new Box<>(5);\n        Box<String> b = new Box<>("Ош");\n        System.out.println(a.get() + " " + b.get());\n    }\n}'),
        Q('Что выведет программа?', ['[кот, пёс, слон]', '[слон, кот, пёс]', '[пёс, кот, слон]', '[слон, пёс, кот]'], 0,
          'Строки сортируются по длине, при равной длине сохраняется исходный порядок (сортировка устойчива).',
          code='List<String> list = new ArrayList<>(List.of("слон", "кот", "пёс"));\nlist.sort(Comparator.comparingInt(String::length));\nSystem.out.println(list);'),
        Q('Что выведет программа?', ['[3, 2, 1]', '[1, 2, 3]', '[2, 1, 3]', '[3, 1, 2]'], 0,
          '`reversed()` меняет порядок компаратора на обратный.',
          code='List<Integer> list = new ArrayList<>(List.of(2, 3, 1));\nlist.sort(Comparator.<Integer>naturalOrder().reversed());\nSystem.out.println(list);'),
        Q('Что выведет программа?', ['true false', 'false true', 'true true', 'false false'], 0,
          '`Predicate` проверяет условие: 4 чётное, 5 нет.',
          code='Predicate<Integer> isEven = n -> n % 2 == 0;\nSystem.out.println(isEven.test(4) + " " + isEven.test(5));'),
        Q('Что выведет программа?', ['7', '12', '3', '4'], 0,
          '`BiFunction` принимает два аргумента и возвращает результат.',
          code='BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;\nSystem.out.println(add.apply(3, 4));'),
        Q('Что произойдёт при компиляции?', ['Ошибка компиляции: переменная должна быть эффективно финальной', 'Выведет 1', 'Выведет 2', 'Выведет 0'], 0,
          'Лямбда не может использовать локальную переменную, значение которой меняется.',
          code='int n = 1;\nn++;\nRunnable r = () -> System.out.println(n);\nr.run();'),
    ],
    videos=[],
    practice=r"""Сортировка пар (значение, номер) — типичная задача для `Comparator`. Решите задачи ниже, не используя ручные сортировки.""",
    problems=[('000300', 'Сортировка по убыванию.'),
              ('000305', 'Ближайшие к нулю: сортировка с компаратором по модулю.')],
    task=('Сортировка студентов', r"""Создайте класс `Student` (имя, группа, средний балл). Отсортируйте список тремя способами: по баллу (`Comparable`), по имени (`Comparator`) и по группе, затем по баллу по убыванию (составной компаратор). Добавьте обобщённый метод `maxBy`, принимающий список и функцию-ключ.

Пришлите код и вывод."""),
    short='дженерики'))
