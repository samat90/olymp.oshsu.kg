# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Исключения', pair(
    'Исключения: try, catch, throw',
    r"""**Исключение** — объект, описывающий ошибку времени выполнения. Если его не обработать, программа завершится с сообщением и «трассировкой стека» (цепочкой вызовов, приведшей к ошибке).

```java
int[] a = new int[3];
System.out.println(a[5]);   // ArrayIndexOutOfBoundsException
```

### try / catch / finally

```java
try {
    int n = Integer.parseInt("12a");
    System.out.println(n);
} catch (NumberFormatException e) {
    System.out.println("не число: " + e.getMessage());
} finally {
    System.out.println("выполнится всегда");
}
```

- блок `try` содержит код, который может вызвать ошибку;
- `catch` перехватывает исключение указанного типа; блоков `catch` может быть несколько, срабатывает первый подходящий. Можно перечислить типы через `|`: `catch (A | B e)`;
- `finally` выполняется всегда: после успешного завершения, после обработанной ошибки и даже при `return`. Туда кладут «уборку».

### Иерархия

Все исключения — наследники `Throwable`. Главные ветви:

- **`Error`** — серьёзные сбои JVM (`OutOfMemoryError`, `StackOverflowError`); их не ловят;
- **`RuntimeException`** и потомки — ошибки программиста: `NullPointerException`, `ArrayIndexOutOfBoundsException`, `ArithmeticException`, `NumberFormatException`, `ClassCastException`; их называют **непроверяемыми** (unchecked);
- **остальные `Exception`** (`IOException`, `FileNotFoundException`) — **проверяемые** (checked): компилятор требует либо перехватить их, либо объявить в сигнатуре метода.

### throws и throw

```java
static void readFile(String path) throws IOException {
    // метод может выбросить IOException; вызывающий обязан обработать
}

static void setAge(int age) {
    if (age < 0) {
        throw new IllegalArgumentException("возраст не может быть отрицательным");
    }
}
```

`throw` выбрасывает исключение, `throws` в заголовке метода предупреждает об исключениях, которые метод не обрабатывает.

### Свои исключения

```java
class NoFuelException extends Exception {
    NoFuelException(String message) { super(message); }
}
```

Наследуясь от `Exception`, получаем проверяемое исключение, от `RuntimeException` — непроверяемое.

### try-with-resources

Ресурсы (файлы, потоки), которые нужно закрывать, объявляют в скобках после `try`; закрытие произойдёт само:

```java
try (BufferedReader br = new BufferedReader(new FileReader("diary.txt"))) {
    System.out.println(br.readLine());
} catch (IOException e) {
    System.out.println("ошибка: " + e.getMessage());
}
```

Ресурс должен реализовать `AutoCloseable`.

### Правила хорошего тона

- ловите конкретные исключения, а не `Exception` и тем более не `Throwable`;
- не оставляйте пустой `catch`: ошибка пропадёт бесследно;
- сообщение об ошибке должно помогать найти причину;
- исключения — для исключительных ситуаций, а не для обычного управления потоком.
""",
    r"""- **Пустой `catch`.** Ошибка исчезает, программа работает «странно». Хотя бы выведите сообщение.
- **Слишком общий `catch (Exception e)`.** Скрывает баги. Указывайте конкретный тип.
- **Порядок `catch`.** Более общий тип нельзя ставить раньше частного: ошибка компиляции «уже перехвачено».
- **Забытое `throws`.** Проверяемое исключение без обработки и без `throws` не скомпилируется.
- **`finally` и `return`.** Код в `finally` выполнится даже после `return` в `try`; `return` в `finally` перекроет исключение.
- **Деление на ноль.** Для целых `ArithmeticException`, для `double` результат `Infinity`.
- **Потеря причины.** При обёртке исключения передавайте исходное: `new RuntimeException("сообщение", e)`.
""",
    [
        Q('Что выведет программа?', ['не число\nконец', 'не число', '12\nконец', 'конец'], 0,
          'Исключение перехвачено, затем выполнился блок `finally`.',
          code='try {\n    Integer.parseInt("12a");\n    System.out.println("ok");\n} catch (NumberFormatException e) {\n    System.out.println("не число");\n} finally {\n    System.out.println("конец");\n}'),
        Q('Что выведет программа?', ['A', 'B', 'A B', 'Ошибка выполнения'], 0,
          'Срабатывает первый подходящий `catch`: `ArithmeticException` — потомок `Exception`, но более частный блок стоит выше.',
          code='try {\n    System.out.println(10 / 0);\n} catch (ArithmeticException e) {\n    System.out.println("A");\n} catch (Exception e) {\n    System.out.println("B");\n}'),
        Q('Что выведет программа?', ['finally\ntry', 'try\nfinally', 'try', 'finally'], 0,
          'Блок `finally` выполняется до того, как значение `return` вернётся вызывающему.',
          code='public class Main {\n    static String f() {\n        try {\n            return "try";\n        } finally {\n            System.out.println("finally");\n        }\n    }\n\n    public static void main(String[] args) {\n        System.out.println(f());\n    }\n}'),
        Q('Что выведет программа?', ['Infinity', '0', 'ArithmeticException', 'Ошибка компиляции'], 0,
          'Деление дробных чисел на ноль исключения не вызывает.',
          code='double a = 1.0;\nSystem.out.println(a / 0);'),
        Q('Что выведет программа?', ['возраст не может быть отрицательным', 'IllegalArgumentException', 'null', 'Ошибка компиляции'], 0,
          '`getMessage()` возвращает текст, переданный в конструктор исключения.',
          code='try {\n    throw new IllegalArgumentException("возраст не может быть отрицательным");\n} catch (IllegalArgumentException e) {\n    System.out.println(e.getMessage());\n}'),
        Q('Что произойдёт при компиляции?', ['Ошибка компиляции: проверяемое исключение не обработано и не объявлено', 'Выведет ok', 'Программа упадёт во время работы', 'Предупреждение'], 0,
          '`IOException` — проверяемое исключение: нужно перехватить его или объявить `throws`.',
          code='public class Main {\n    static void read() throws java.io.IOException {\n        throw new java.io.IOException("нет файла");\n    }\n\n    public static void main(String[] args) {\n        read();\n    }\n}'),
    ],
    videos=[('fH6G8KrjElk', 'Видео: исключения и обобщённые типы', 'Проверяемые исключения, `finally`, `try-with-resources` и начало темы про дженерики.'),
            ('KLAf5EEdZ-s', 'Видео: собственные исключения и оператор throw', 'Как создавать собственные исключения.')],
    practice=r"""Практика: читать входные данные надёжно. Программа не должна падать при неверном вводе.""",
    problems=[('000205', 'Второй максимум: подумайте, что делать, если все числа одинаковые.')],
    task=('Безопасный калькулятор', r"""Калькулятор читает числа и операцию. Неверное число — просит повторить (`NumberFormatException`), деление на ноль — понятное сообщение, неизвестная операция — собственное исключение `BadOperationException` (проверяемое). Используйте `try-catch-finally`.

Пришлите код и примеры «плохого» ввода."""),
    short='исключения'))
