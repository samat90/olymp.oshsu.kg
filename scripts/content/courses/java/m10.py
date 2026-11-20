# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Наследование, интерфейсы, полиморфизм', pair(
    'Наследование, абстрактные классы и интерфейсы',
    r"""### Наследование

```java
class Animal {
    protected String name;

    Animal(String name) { this.name = name; }

    void eat() { System.out.println(name + " ест"); }
    void speak() { System.out.println(name + " издаёт звук"); }
}

class Dog extends Animal {
    Dog(String name) {
        super(name);                 // вызов конструктора родителя
    }

    @Override
    void speak() { System.out.println(name + ": гав"); }
}
```

`extends` означает, что `Dog` унаследовал поля и методы `Animal`. `super(...)` вызывает конструктор родителя и должен идти первой строкой. Метод можно **переопределить** в потомке; аннотация `@Override` просит компилятор проверить, что метод действительно переопределяет родительский (опечатка станет ошибкой). Обратиться к родительской версии можно через `super.speak()`.

Класс наследует только от одного класса. Все классы неявно наследуют `Object`, поэтому у любого объекта есть `toString`, `equals`, `hashCode`.

### Полиморфизм

Переменной родительского типа можно присвоить объект потомка. Метод выбирается по **настоящему типу объекта** во время выполнения:

```java
Animal a = new Dog("Бобик");
a.speak();      // Бобик: гав
```

Это работает, потому что в Java все обычные методы «виртуальные». Благодаря этому можно написать код, работающий с общим типом:

```java
Animal[] zoo = { new Dog("Бобик"), new Cat("Мурка"), new Animal("Кто-то") };
for (Animal x : zoo) x.speak();   // у каждого своя реализация
```

Проверить тип: `x instanceof Dog`. Привести: `Dog d = (Dog) x;` (если тип не подходит, `ClassCastException`). Современная запись: `if (x instanceof Dog d) { d.bark(); }`.

### Абстрактные классы

Класс, у которого есть неполная часть:

```java
abstract class Shape {
    abstract double area();           // без тела
    void describe() { System.out.println("Площадь: " + area()); }
}

class Circle extends Shape {
    double r;
    Circle(double r) { this.r = r; }
    double area() { return Math.PI * r * r; }
}
```

Объект абстрактного класса создать нельзя. Потомок обязан реализовать все абстрактные методы.

### Интерфейсы

Интерфейс описывает набор методов, которые класс обязуется реализовать:

```java
interface Flyable {
    void fly();
    default void land() { System.out.println("приземлился"); }
}

class Bird extends Animal implements Flyable {
    Bird(String name) { super(name); }
    public void fly() { System.out.println(name + " летит"); }
}
```

Класс может реализовывать **много** интерфейсов. Методы интерфейса по умолчанию публичные. Метод с `default` имеет реализацию по умолчанию, `static` — вспомогательные функции.

### Что выбрать

| ситуация | выбор |
|---|---|
| нужно описать «умение» (может летать, сравниваться) | интерфейс |
| есть общее состояние и частичная реализация | абстрактный класс |
| нужна отдельная иерархия «является» | наследование |

Часто интерфейсы дают более гибкий дизайн, а наследование стоит применять осторожно: «предпочитайте композицию наследованию».

### final

`final class X` запрещает наследование. `final void f()` запрещает переопределение. `String` и `Integer` — финальные классы.

### Модификаторы доступа

`public` — всем; `protected` — потомкам и своему пакету; без модификатора — только своему пакету; `private` — только своему классу.
""",
    r"""- **Забыли `super(...)` в конструкторе.** Если у родителя нет конструктора без параметров, потомок не скомпилируется.
- **Опечатка в переопределённом методе.** Без `@Override` метод тихо станет новым. Всегда ставьте аннотацию.
- **Сужение доступа.** Нельзя переопределить публичный метод с более слабым доступом.
- **Приведение типов.** `(Dog) animal` для кота даёт `ClassCastException`. Проверяйте `instanceof`.
- **Поля не полиморфны.** Обращение по ссылке родительского типа читает поле родителя, а не потомка.
- **Вызов переопределяемого метода из конструктора.** Метод потомка может увидеть ещё не готовый объект.
- **Метод интерфейса не `public`** в реализации: нужно писать `public`.
""",
    [
        Q('Что выведет программа?', ['Бобик: гав', 'Бобик издаёт звук', 'Бобик', 'Ошибка компиляции'], 0,
          'Метод выбирается по настоящему типу объекта (`Dog`), а не по типу переменной.',
          code='public class Main {\n    static class Animal {\n        String name;\n        Animal(String name) { this.name = name; }\n        void speak() { System.out.println(name + " издаёт звук"); }\n    }\n    static class Dog extends Animal {\n        Dog(String name) { super(name); }\n        @Override void speak() { System.out.println(name + ": гав"); }\n    }\n\n    public static void main(String[] args) {\n        Animal a = new Dog("Бобик");\n        a.speak();\n    }\n}'),
        Q('Что выведет программа?', ['A B', 'B A', 'A', 'B'], 0,
          'Конструктор родителя вызывается раньше конструктора потомка.',
          code='public class Main {\n    static class A { A() { System.out.print("A "); } }\n    static class B extends A { B() { System.out.print("B"); } }\n\n    public static void main(String[] args) {\n        new B();\n    }\n}'),
        Q('Что выведет программа?', ['12.00', '3.14', '0.00', 'Ошибка компиляции'], 0,
          'Метод `area` абстрактного класса реализован в потомке и вызван полиморфно.',
          code='public class Main {\n    static abstract class Shape { abstract double area(); }\n    static class Rect extends Shape {\n        double w = 3, h = 4;\n        double area() { return w * h; }\n    }\n\n    public static void main(String[] args) {\n        Shape s = new Rect();\n        System.out.printf(java.util.Locale.US, "%.2f%n", s.area());\n    }\n}'),
        Q('Что выведет программа?', ['летит приземлился', 'приземлился летит', 'летит', 'приземлился'], 0,
          'Метод `land` берётся из интерфейса (реализация по умолчанию), а `fly` реализован в классе.',
          code='public class Main {\n    interface Flyable {\n        void fly();\n        default void land() { System.out.print("приземлился"); }\n    }\n    static class Bird implements Flyable {\n        public void fly() { System.out.print("летит "); }\n    }\n\n    public static void main(String[] args) {\n        Bird b = new Bird();\n        b.fly();\n        b.land();\n    }\n}'),
        Q('Что выведет программа?', ['A', 'B', 'AB', 'Ошибка компиляции'], 0,
          'Поля не полиморфны: доступ идёт по типу переменной (`A`).',
          code='public class Main {\n    static class A { String name = "A"; }\n    static class B extends A { String name = "B"; }\n\n    public static void main(String[] args) {\n        A x = new B();\n        System.out.println(x.name);\n    }\n}'),
        Q('Что произойдёт при компиляции?', ['Ошибка компиляции: нельзя создать экземпляр абстрактного класса', 'Выведет 0', 'Выведет 3.14', 'Предупреждение'], 0,
          'Объекты абстрактных классов создавать нельзя.',
          code='public class Main {\n    static abstract class Shape { abstract double area(); }\n\n    public static void main(String[] args) {\n        Shape s = new Shape();\n        System.out.println(s.area());\n    }\n}'),
    ],
    videos=[('5Ai4tXThcHM', 'Видео: ООП в Java', 'Вебинар по ООП: наследование, полиморфизм, инкапсуляция, интерфейсы.'),
            ('vdUDAzBp5PE', 'Видео: абстрактный класс', 'Что такое абстрактный класс и чем он отличается от обычного класса и интерфейса.')],
    practice=r"""Лучшая практика ООП — проект с несколькими взаимодействующими классами. Выполните задание ниже.""",
    problems=[],
    task=('Зоопарк фигур и животных', r"""Часть 1: абстрактный класс `Shape` (`area`, `perimeter`) и три фигуры. Найдите фигуру с наибольшей площадью и суммарную площадь.

Часть 2: иерархия `Animal`, `Dog`, `Cat`, интерфейс `Swimmer`, который реализуют некоторые из них. Выведите, кто что умеет, используя `instanceof`.

Пришлите код и вывод."""),
    short='ООП'))
