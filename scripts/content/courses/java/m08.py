# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Методы', pair(
    'Методы',
    r"""В Java функции называются **методами** и всегда принадлежат классу. Пока мы пишем статические методы внутри `Main`.

```java
public class Main {
    static int area(int w, int h) {
        return w * h;
    }

    public static void main(String[] args) {
        System.out.println(area(4, 5));
    }
}
```

Объявление: модификаторы, тип результата, имя, параметры в скобках. Метод, ничего не возвращающий, имеет тип `void`. Порядок методов в классе значения не имеет.

### Передача по значению

Java **всегда** передаёт аргументы по значению: метод получает копию. Для примитивов это означает, что оригинал не изменится:

```java
static void inc(int x) { x++; }
int a = 5;
inc(a);
System.out.println(a);   // 5
```

Для объектов копируется **ссылка**: метод может изменить содержимое объекта (элементы массива, поля), но не может заставить внешнюю переменную указывать на другой объект:

```java
static void change(int[] arr) { arr[0] = 99; }       // изменит оригинал
static void replace(int[] arr) { arr = new int[]{7}; } // оригинал не затронет
```

### Перегрузка

Несколько методов с одним именем, но разными параметрами:

```java
static int add(int a, int b) { return a + b; }
static double add(double a, double b) { return a + b; }
static int add(int a, int b, int c) { return a + b + c; }
```

Компилятор выбирает метод по типам аргументов. Различие только в типе результата перегрузкой не считается.

### Переменное число аргументов

```java
static int sum(int... nums) {
    int total = 0;
    for (int n : nums) total += n;
    return total;
}
sum();           // 0
sum(1, 2, 3);    // 6
```

Внутри `nums` — обычный массив.

### Рекурсия

```java
static long fact(int n) {
    return n <= 1 ? 1 : n * fact(n - 1);
}
```

Каждый вызов занимает место в стеке. При слишком большой глубине (порядка десятков тысяч) произойдёт `StackOverflowError`.

### Возврат нескольких значений

Метод возвращает одно значение. Если нужно несколько, возвращают массив, список или объект (`record`, класс):

```java
record Result(int quotient, int remainder) {}

static Result divmod(int a, int b) {
    return new Result(a / b, a % b);
}
Result r = divmod(17, 5);
System.out.println(r.quotient() + " " + r.remainder());  // 3 2
```

### static и обычные методы

`static`-метод принадлежит классу и вызывается без объекта. Обычный метод вызывается у объекта. Из `static`-метода нельзя напрямую обращаться к обычным полям и методам: нет объекта. Подробнее — в модуле про классы.

### Область видимости

Переменная существует в том блоке `{ ... }`, где объявлена. Объявить в блоке переменную с именем уже существующей локальной переменной нельзя.
""",
    r"""- **Ожидание, что метод изменит примитив.** Передаётся копия. Верните результат: `x = inc(x);`.
- **Присваивание параметру-ссылке** не влияет на внешнюю переменную. Менять можно содержимое.
- **Метод без `return`.** Для не-`void` метода все пути должны возвращать значение, иначе ошибка компиляции.
- **Рекурсия без базового случая:** `StackOverflowError`.
- **Вызов обычного метода из `static main`** без объекта: ошибка «non-static method cannot be referenced from a static context».
- **Перегрузка и автоприведение.** `f(5)` при методах `f(long)` и `f(Integer)` выберет `f(long)`: расширение выгоднее упаковки.
""",
    [
        Q('Что выведет программа?', ['5', '6', '0', 'Ошибка'], 0,
          'Метод получает копию числа и оригинал не меняет.',
          code='public class Main {\n    static void inc(int x) { x++; }\n\n    public static void main(String[] args) {\n        int a = 5;\n        inc(a);\n        System.out.println(a);\n    }\n}'),
        Q('Что выведет программа?', ['99', '1', '0', 'Ошибка'], 0,
          'Через ссылку на массив метод меняет содержимое оригинального массива.',
          code='public class Main {\n    static void change(int[] arr) { arr[0] = 99; }\n\n    public static void main(String[] args) {\n        int[] a = {1, 2};\n        change(a);\n        System.out.println(a[0]);\n    }\n}'),
        Q('Что выведет программа?', ['1', '99', '7', 'Ошибка'], 0,
          'Присваивание параметру нового массива меняет только локальную ссылку. Внешняя переменная указывает на прежний массив.',
          code='public class Main {\n    static void replace(int[] arr) { arr = new int[]{99}; }\n\n    public static void main(String[] args) {\n        int[] a = {1, 2};\n        replace(a);\n        System.out.println(a[0]);\n    }\n}'),
        Q('Что выведет программа?', ['0 6', '6 0', '0 0', '3 6'], 0,
          'Метод с переменным числом аргументов принимает любое количество, в том числе ноль.',
          code='public class Main {\n    static int sum(int... nums) {\n        int total = 0;\n        for (int n : nums) total += n;\n        return total;\n    }\n\n    public static void main(String[] args) {\n        System.out.println(sum() + " " + sum(1, 2, 3));\n    }\n}'),
        Q('Что выведет программа?', ['3 2', '2 3', '3.4 2', '17 5'], 0,
          'Метод возвращает объект `record` с двумя полями.',
          code='public class Main {\n    record Result(int quotient, int remainder) {}\n\n    static Result divmod(int a, int b) {\n        return new Result(a / b, a % b);\n    }\n\n    public static void main(String[] args) {\n        Result r = divmod(17, 5);\n        System.out.println(r.quotient() + " " + r.remainder());\n    }\n}'),
        Q('Что выведет программа?', ['24', '10', '16', '4'], 0,
          '`4 * 3 * 2 * 1`.',
          code='public class Main {\n    static int fact(int n) {\n        return n <= 1 ? 1 : n * fact(n - 1);\n    }\n\n    public static void main(String[] args) {\n        System.out.println(fact(4));\n    }\n}'),
    ],
    videos=[],
    practice=r"""Разбивайте решение на небольшие методы. Для типов, которые нужно вернуть парой, подойдёт `record`.""",
    problems=[('000069', 'НОД: алгоритм Евклида, можно рекурсией.'),
              ('000070', 'НОК через НОД.'),
              ('000683', 'Обратное число.'),
              ('000682', 'Перевод в двоичную систему.')],
    task=('Набор методов', r"""Напишите методы `isPrime`, `digitsSum`, `fib` (рекурсивно и в цикле), `wordCount`, `stats` (минимум, максимум и среднее в виде `record`). Продемонстрируйте каждый на нескольких примерах.

Пришлите код и вывод."""),
    short='методы'))
