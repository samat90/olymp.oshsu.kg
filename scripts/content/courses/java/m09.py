# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Классы и объекты', pair(
    'Классы, конструкторы и инкапсуляция',
    r"""Класс описывает тип объектов: какие у них данные (поля) и что они умеют (методы). Объект — конкретный экземпляр класса.

```java
public class Horse {
    private String name;
    private int age;

    public Horse(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public String getName() { return name; }
    public int getAge() { return age; }

    public void birthday() {
        age++;
    }

    @Override
    public String toString() {
        return name + ", " + age + " лет";
    }
}
```

Использование:

```java
Horse h = new Horse("Тулпар", 5);
h.birthday();
System.out.println(h);        // Тулпар, 6 лет
```

### Разбор

- **Поля** (`name`, `age`) хранят состояние. Модификатор `private` закрывает доступ извне: это называется **инкапсуляцией**. Снаружи с полем работают через методы (геттеры и сеттеры), которые могут проверять значения.
- **Конструктор** — особый метод с именем класса и без типа результата. Он вызывается при создании объекта через `new`.
- **`this`** — ссылка на текущий объект. Нужна, когда имя параметра совпадает с именем поля.
- **`toString()`** определяет, как объект превращается в строку (для `println` и склейки).
- Конструкторов может быть несколько (перегрузка). Если не написать ни одного, Java создаст пустой.

### Ссылки и null

Переменная объектного типа хранит **ссылку**. Значение `null` означает «ссылка ни на что не указывает». Вызов метода у `null` даёт `NullPointerException`.

```java
Horse a = new Horse("Тулпар", 5);
Horse b = a;        // вторая ссылка на тот же объект
b.birthday();
System.out.println(a.getAge());  // 6
```

### static: общее для класса

```java
public class Account {
    private static int count = 0;   // один на все объекты
    public Account() { count++; }
    public static int getCount() { return count; }
}
```

`static`-члены принадлежат классу, а не объекту: `Account.getCount()`. Метод `main` тоже статический.

### equals и hashCode

Оператор `==` сравнивает ссылки. Чтобы сравнивать по содержимому, переопределяют `equals`, а вместе с ним `hashCode` (иначе объекты будут вести себя неправильно в `HashMap` и `HashSet`):

```java
@Override
public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof Horse)) return false;
    Horse other = (Horse) o;
    return age == other.age && name.equals(other.name);
}

@Override
public int hashCode() {
    return Objects.hash(name, age);
}
```

### record

Для простых «носителей данных» с Java 16 есть `record`: компилятор сам создаст конструктор, геттеры, `equals`, `hashCode` и `toString`:

```java
record Point(int x, int y) {}

Point p = new Point(3, 4);
System.out.println(p.x() + " " + p);    // 3 Point[x=3, y=4]
```

Поля record неизменяемы.

### Пакеты и файлы

Каждый публичный класс лежит в отдельном файле с совпадающим именем. Классы группируют в пакеты (`package com.example;`). Для школьных задач достаточно одного файла: остальные классы объявляют без `public` рядом с `Main`.
""",
    r"""- **`NullPointerException`.** Объект не создан (`Horse h;` без `new`) или метод вернул `null`. Проверяйте перед использованием.
- **`==` вместо `equals`.** Для объектов сравнивает ссылки.
- **Переопределили `equals` без `hashCode`.** Объекты «теряются» в `HashMap` и `HashSet`.
- **Публичные поля.** Любой может записать неверное значение. Делайте поля приватными и проверяйте в методах.
- **Забыли `this`.** `name = name;` в конструкторе присваивает параметр самому себе, поле остаётся `null`.
- **Конструктор с типом результата.** `public void Horse()` — это обычный метод, а не конструктор.
- **Изменяемые поля в `record`.** Если в record лежит список, сам record остаётся неизменяемым, а список — нет.
""",
    [
        Q('Что выведет программа?', ['Тулпар, 6 лет', 'Тулпар, 5 лет', 'Horse@1b6d3586', 'Ошибка компиляции'], 0,
          '`toString` определяет текстовое представление объекта.',
          code='public class Main {\n    static class Horse {\n        String name; int age;\n        Horse(String name, int age) { this.name = name; this.age = age; }\n        void birthday() { age++; }\n        public String toString() { return name + ", " + age + " лет"; }\n    }\n\n    public static void main(String[] args) {\n        Horse h = new Horse("Тулпар", 5);\n        h.birthday();\n        System.out.println(h);\n    }\n}'),
        Q('Что выведет программа?', ['6 6', '5 6', '6 5', '5 5'], 0,
          'Обе переменные ссылаются на один и тот же объект.',
          code='public class Main {\n    static class Box { int n = 5; }\n\n    public static void main(String[] args) {\n        Box a = new Box();\n        Box b = a;\n        b.n++;\n        System.out.println(a.n + " " + b.n);\n    }\n}'),
        Q('Что выведет программа?', ['3', '1', '0', '2'], 0,
          'Статическое поле общее для всех объектов.',
          code='public class Main {\n    static class A {\n        static int count = 0;\n        A() { count++; }\n    }\n\n    public static void main(String[] args) {\n        new A();\n        new A();\n        new A();\n        System.out.println(A.count);\n    }\n}'),
        Q('Что выведет программа?', ['false true', 'true true', 'true false', 'false false'], 0,
          'Для двух разных объектов `==` ложно, а переопределённый `equals` сравнивает значения полей.',
          code='public class Main {\n    static class P {\n        int x;\n        P(int x) { this.x = x; }\n        @Override public boolean equals(Object o) { return o instanceof P p && p.x == x; }\n        @Override public int hashCode() { return x; }\n    }\n\n    public static void main(String[] args) {\n        P a = new P(1), b = new P(1);\n        System.out.println((a == b) + " " + a.equals(b));\n    }\n}'),
        Q('Что выведет программа?', ['3 Point[x=3, y=4]', 'Point[x=3, y=4]', '3 Point@4', 'Ошибка компиляции'], 0,
          '`record` автоматически получает геттеры `x()` и `y()` и метод `toString`.',
          code='public class Main {\n    record Point(int x, int y) {}\n\n    public static void main(String[] args) {\n        Point p = new Point(3, 4);\n        System.out.println(p.x() + " " + p);\n    }\n}'),
        Q('Что выведет программа?', ['null', '0', 'Ошибка компиляции', 'NullPointerException'], 0,
          'В конструкторе `name = name;` присваивает параметр самому себе, поэтому поле осталось `null`. Так выглядит забытый `this`.',
          code='public class Main {\n    static class A {\n        String name;\n        A(String name) { name = name; }\n    }\n\n    public static void main(String[] args) {\n        System.out.println(new A("Ош").name);\n    }\n}'),
    ],
    videos=[],
    practice=r"""Классы в задачах сайта встречаются редко, но удобны для хранения связанных данных (например, пара «имя и балл» при сортировке).""",
    problems=[],
    task=('Банковский счёт', r"""Класс `Account`: владелец, баланс (приватные поля), конструктор, методы `deposit`, `withdraw` (бросает исключение при нехватке денег), `getBalance`, `toString`, статический счётчик созданных счетов. Переопределите `equals` и `hashCode` по номеру счёта.

Создайте два счёта, выполните операции, покажите обработку ошибки. Пришлите код и вывод."""),
    short='классы'))
