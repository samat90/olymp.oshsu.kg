# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Классы и наследование', pair(
    'Классы, наследование, this',
    r"""Синтаксис `class` появился в JavaScript в 2015 году. Под капотом язык по-прежнему использует прототипы, но для повседневной работы нового синтаксиса достаточно.

```javascript
class Horse {
  constructor(name, age) {
    this.name = name;
    this.age = age;
  }

  birthday() {
    this.age++;
  }

  toString() {
    return `${this.name}, ${this.age} лет`;
  }
}

const h = new Horse("Тулпар", 5);
h.birthday();
console.log(String(h));    // Тулпар, 6 лет
console.log(h instanceof Horse);   // true
```

- `constructor` вызывается при создании объекта через `new`;
- `this` внутри метода — объект, у которого его вызвали;
- методы лежат в классе, а не копируются в каждый объект.

### Геттеры и сеттеры

```javascript
class Account {
  #balance = 0;                      // приватное поле

  get balance() { return this.#balance; }

  deposit(amount) {
    if (amount <= 0) throw new RangeError("сумма должна быть положительной");
    this.#balance += amount;
  }
}

const a = new Account();
a.deposit(100);
console.log(a.balance);    // 100
// console.log(a.#balance); // SyntaxError: поле приватное
```

Имена, начинающиеся с `#`, доступны только внутри класса. Это настоящая инкапсуляция.

### static

```javascript
class Counter {
  static count = 0;
  constructor() { Counter.count++; }
  static create() { return new Counter(); }
}
new Counter(); Counter.create();
console.log(Counter.count);   // 2
```

### Наследование

```javascript
class Animal {
  constructor(name) { this.name = name; }
  speak() { return `${this.name} издаёт звук`; }
}

class Dog extends Animal {
  constructor(name) {
    super(name);                    // вызов конструктора родителя
  }
  speak() {
    return `${super.speak()}: гав`;
  }
}

const d = new Dog("Бобик");
console.log(d.speak());   // Бобик издаёт звук: гав
```

`extends` задаёт родителя. В конструкторе потомка `super(...)` нужно вызвать **до** обращения к `this`. Метод потомка переопределяет метод родителя, а `super.метод()` обращается к родительской версии.

### Полиморфизм

```javascript
const zoo = [new Dog("Бобик"), new Animal("Кто-то")];
for (const a of zoo) console.log(a.speak());   // у каждого своя версия
```

В JavaScript достаточно, чтобы у объекта был нужный метод («утиная типизация»): общий родитель не обязателен.

### Потеря this

`this` определяется тем, как функцию **вызвали**, а не где она написана:

```javascript
const speak = d.speak;
// speak();            // TypeError: this равно undefined
const bound = d.speak.bind(d);   // привязать
console.log(bound());
```

Стрелочные функции берут `this` из окружения, поэтому внутри методов их удобно использовать для обработчиков и колбэков:

```javascript
class Timer {
  constructor() { this.ticks = 0; }
  start() {
    setInterval(() => this.ticks++, 1000);   // this — объект Timer
  }
}
```

### Прототипы

Каждый объект ссылается на прототип, откуда берёт недостающие свойства и методы. Классы — «красивая обёртка» над этим механизмом: методы класса лежат в `Класс.prototype`. Проверка: `Object.getPrototypeOf(h) === Horse.prototype`.
""",
    r"""- **Забыли `new`.** `Horse("Тулпар", 5)` без `new` вызовет ошибку (классы нельзя вызывать как функции).
- **Забыли `super(...)`.** В конструкторе потомка обращение к `this` до `super` бросает `ReferenceError`.
- **Потеря `this`.** Метод, переданный как колбэк (`setTimeout(obj.method)`), теряет объект. Используйте стрелку или `bind`.
- **Публичное поле, которое хотели скрыть.** Соглашение `_name` не защищает данные; настоящая защита — `#name`.
- **Методы-стрелки в классе** создаются для каждого объекта заново и не наследуются как обычные методы.
- **Изменяемые значения в статических полях** общие для всех экземпляров.
""",
    [
        Q('Что выведет программа?', ['Тулпар, 6 лет', 'Тулпар, 5 лет', '[object Object]', 'Ошибка'], 0,
          'Метод `toString` определяет строковое представление; `birthday` увеличил возраст.',
          code='class Horse {\n  constructor(name, age) { this.name = name; this.age = age; }\n  birthday() { this.age++; }\n  toString() { return `${this.name}, ${this.age} лет`; }\n}\nconst h = new Horse("Тулпар", 5);\nh.birthday();\nconsole.log(String(h));'),
        Q('Что выведет программа?', ['Бобик издаёт звук: гав', 'Бобик: гав', 'Бобик издаёт звук', 'undefined'], 0,
          '`super.speak()` вызывает метод родителя, потомок добавляет своё.',
          code='class Animal {\n  constructor(name) { this.name = name; }\n  speak() { return `${this.name} издаёт звук`; }\n}\nclass Dog extends Animal {\n  speak() { return `${super.speak()}: гав`; }\n}\nconsole.log(new Dog("Бобик").speak());'),
        Q('Что выведет программа?', ['2', '1', '0', 'undefined'], 0,
          'Статическое поле общее для класса: конструктор увеличивает его при каждом создании.',
          code='class Counter {\n  static count = 0;\n  constructor() { Counter.count++; }\n}\nnew Counter();\nnew Counter();\nconsole.log(Counter.count);'),
        Q('Что выведет программа?', ['100 undefined', '100 100', 'undefined 100', 'Ошибка'], 0,
          'Приватное поле `#balance` недоступно снаружи: обращение `a.balance2` просто несуществующее свойство. Через геттер значение читается.',
          code='class Account {\n  #balance = 0;\n  get balance() { return this.#balance; }\n  deposit(x) { this.#balance += x; }\n}\nconst a = new Account();\na.deposit(100);\nconsole.log(a.balance, a.balance2);'),
        Q('Что выведет программа?', ['TypeError', 'Бобик', 'undefined', 'ReferenceError'], 0,
          'Метод вызван отдельно от объекта, и `this` внутри него не определён.',
          code='class Dog {\n  constructor(n) { this.name = n; }\n  say() { return this.name; }\n}\nconst d = new Dog("Бобик");\nconst f = d.say;\ntry {\n  console.log(f());\n} catch (e) {\n  console.log(e.name);\n}'),
        Q('Что выведет программа?', ['Бобик', 'TypeError', 'undefined', 'Ошибка синтаксиса'], 0,
          '`bind` привязывает `this`, и метод работает отдельно от объекта.',
          code='class Dog {\n  constructor(n) { this.name = n; }\n  say() { return this.name; }\n}\nconst d = new Dog("Бобик");\nconst f = d.say.bind(d);\nconsole.log(f());'),
        Q('Что выведет программа?', ['true true false', 'true false false', 'false true true', 'true true true'], 0,
          '`instanceof` учитывает наследование: `Dog` — потомок `Animal`.',
          code='class Animal {}\nclass Dog extends Animal {}\nconst d = new Dog();\nconsole.log(d instanceof Dog, d instanceof Animal, d instanceof Array);'),
    ],
    videos=[],
    practice=r"""Классы пригодятся для хранения связанных данных и логики. Основное упражнение этого модуля — задание.""",
    problems=[],
    task=('Банковский счёт', r"""Класс `Account`: владелец, приватный баланс (`#balance`), геттер `balance`, методы `deposit` и `withdraw` (бросает собственную ошибку при нехватке денег), `toString`, статический счётчик созданных счетов. Класс-наследник `SavingsAccount` добавляет проценты.

Создайте два счёта, выполните операции, покажите обработку ошибки. Пришлите код и вывод."""),
    short='классы'))
