# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Наследование, интерфейсы, полиморфизм', pair(
    'Наследование, virtual, abstract и интерфейсы',
    r"""### Наследование

```csharp
class Animal
{
    protected string name;
    public Animal(string name) { this.name = name; }

    public void Eat() { Console.WriteLine(name + " ест"); }
    public virtual void Speak() { Console.WriteLine(name + " издаёт звук"); }
}

class Dog : Animal
{
    public Dog(string name) : base(name) { }    // вызов конструктора базового класса

    public override void Speak() { Console.WriteLine(name + ": гав"); }
}
```

`class Dog : Animal` означает, что `Dog` унаследовал от `Animal` всё, кроме приватного. Конструктор базового класса вызывают через `: base(...)`. Класс наследует от **одного** класса, но может реализовывать много интерфейсов. Все классы неявно наследуют `object`: поэтому у любого объекта есть `ToString`, `Equals`, `GetHashCode`.

### virtual и override

Чтобы метод можно было переопределить, в базовом классе его помечают `virtual`, а в потомке пишут `override`. Если `virtual` нет, переопределить метод нельзя.

### Полиморфизм

Переменной базового типа можно присвоить объект потомка. Метод `virtual` выбирается по **настоящему типу объекта** во время выполнения:

```csharp
Animal a = new Dog("Бобик");
a.Speak();       // Бобик: гав
```

```csharp
Animal[] zoo = { new Dog("Бобик"), new Cat("Мурка"), new Animal("Кто-то") };
foreach (Animal x in zoo) x.Speak();   // у каждого своя реализация
```

Проверка и приведение типа: `if (x is Dog d) d.Bark();`, `Dog d = x as Dog;` (вернёт `null`, если не подходит), `(Dog)x` (при несовпадении `InvalidCastException`).

### Абстрактные классы

```csharp
abstract class Shape
{
    public abstract double Area();                 // без тела
    public void Describe() { Console.WriteLine("Площадь: " + Area()); }
}

class Circle : Shape
{
    private double r;
    public Circle(double r) { this.r = r; }
    public override double Area() { return Math.PI * r * r; }
}
```

Экземпляр абстрактного класса создать нельзя. Потомок обязан реализовать все абстрактные члены.

### Интерфейсы

Интерфейс задаёт набор членов, которые класс обязуется реализовать:

```csharp
interface IFlyable
{
    void Fly();
}

class Bird : Animal, IFlyable
{
    public Bird(string name) : base(name) { }
    public void Fly() { Console.WriteLine(name + " летит"); }
}
```

Имена интерфейсов принято начинать с `I`. Через переменную типа интерфейса можно работать с любым реализующим классом: `IFlyable f = new Bird("Орёл"); f.Fly();`.

### Запрет наследования и сокрытие

`sealed class X` запрещает наследование. Ключевое слово `new` перед методом в потомке **скрывает** унаследованный метод вместо переопределения: тогда вызов зависит от типа ссылки. Этого стоит избегать.

### Композиция

Наследование выражает отношение «является» (собака — животное). Для отношения «имеет» (у машины есть двигатель) храните один объект в другом. «Предпочитайте композицию наследованию».
""",
    r"""- **Забыли `virtual`/`override`.** Без них метод не переопределяется, а сокрывается (`new`): результат зависит от типа переменной.
- **Забыли `: base(...)`.** Если у базового класса нет конструктора без параметров, потомок не скомпилируется.
- **Приведение `(Dog)animal`** для кота даёт `InvalidCastException`. Используйте `is` или `as`.
- **Вызов виртуального метода из конструктора** может обратиться к ещё не готовому потомку.
- **Реализация интерфейса без `public`.** Члены интерфейса должны быть публичными.
- **Слишком глубокая иерархия.** Усложняет понимание; ограничивайтесь двумя-тремя уровнями.
""",
    [
        Q('Что выведет программа?', ['Бобик: гав', 'Бобик издаёт звук', 'Бобик', 'Ошибка компиляции'], 0,
          '`Speak` помечен `virtual` и переопределён, поэтому вызывается версия настоящего типа `Dog`.',
          code='class Animal\n{\n    protected string name;\n    public Animal(string name) { this.name = name; }\n    public virtual void Speak() { Console.WriteLine(name + " издаёт звук"); }\n}\n\nclass Dog : Animal\n{\n    public Dog(string name) : base(name) { }\n    public override void Speak() { Console.WriteLine(name + ": гав"); }\n}\n\nclass P\n{\n    static void Main()\n    {\n        Animal a = new Dog("Бобик");\n        a.Speak();\n    }\n}'),
        Q('Что выведет программа?', ['A B', 'B A', 'A', 'B'], 0,
          'Конструктор базового класса вызывается раньше конструктора потомка.',
          code='class A { public A() { Console.Write("A "); } }\nclass B : A { public B() { Console.Write("B"); } }\n\nclass P\n{\n    static void Main()\n    {\n        new B();\n    }\n}'),
        Q('Что выведет программа?', ['звук', 'гав', 'звук гав', 'Ошибка компиляции'], 0,
          'Метод в базовом классе не `virtual`, поэтому метод потомка лишь скрывает его (`new`). Вызов по ссылке базового типа выбирает метод базового класса.',
          code='class Animal { public void Speak() { Console.Write("звук"); } }\nclass Dog : Animal { public new void Speak() { Console.Write("гав"); } }\n\nclass P\n{\n    static void Main()\n    {\n        Animal a = new Dog();\n        a.Speak();\n    }\n}'),
        Q('Что выведет программа?', ['12.00', '3.14', '0.00', 'Ошибка компиляции'], 0,
          'Абстрактный метод реализован в потомке и вызван полиморфно.',
          code='abstract class Shape { public abstract double Area(); }\nclass Rect : Shape\n{\n    public override double Area() { return 3 * 4; }\n}\n\nclass P\n{\n    static void Main()\n    {\n        Shape s = new Rect();\n        Console.WriteLine(s.Area().ToString("F2"));\n    }\n}'),
        Q('Что выведет программа?', ['летит', 'ничего', 'Ошибка компиляции', 'Ошибка выполнения'], 0,
          'Класс реализует интерфейс, поэтому через переменную интерфейса можно вызвать `Fly`.',
          code='interface IFlyable { void Fly(); }\nclass Bird : IFlyable { public void Fly() { Console.WriteLine("летит"); } }\n\nclass P\n{\n    static void Main()\n    {\n        IFlyable f = new Bird();\n        f.Fly();\n    }\n}'),
        Q('Что произойдёт при компиляции?', ['Ошибка компиляции: нельзя создать экземпляр абстрактного класса', 'Выведет 0', 'Выведет Shape', 'Предупреждение'], 0,
          'Объекты абстрактных классов создавать нельзя.',
          code='abstract class Shape { public abstract double Area(); }\n\nclass P\n{\n    static void Main()\n    {\n        Shape s = new Shape();\n        Console.WriteLine(s.Area());\n    }\n}'),
    ],
    videos=[],
    practice=r"""Лучшая практика ООП — проект с несколькими взаимодействующими классами. Выполните задание ниже.""",
    problems=[],
    task=('Зоопарк фигур и животных', r"""Часть 1: абстрактный класс `Shape` (`Area`, `Perimeter`) и три фигуры. Найдите фигуру с наибольшей площадью и суммарную площадь.

Часть 2: иерархия `Animal`, `Dog`, `Cat`, интерфейс `ISwimmer`, который реализуют некоторые из них. Выведите, кто что умеет, используя `is`.

Пришлите код и вывод."""),
    short='ООП'))
