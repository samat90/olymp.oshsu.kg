# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Ошибки', pair(
    'Ошибки: try, catch, throw',
    r"""Если в программе возникает ошибка, JavaScript создаёт объект ошибки и «бросает» его. Если ошибку не перехватить, выполнение остановится (в браузере только текущий скрипт, в Node.js — вся программа).

```javascript
console.log(user.name);   // ReferenceError: user is not defined
```

### try / catch / finally

```javascript
try {
  const data = JSON.parse("не json");
  console.log(data);
} catch (error) {
  console.log("ошибка:", error.name);
} finally {
  console.log("выполнится всегда");
}
```

- в `try` помещают код, который может вызвать ошибку;
- `catch` получает объект ошибки; свойства `name` (тип), `message` (текст), `stack` (цепочка вызовов);
- `finally` выполняется всегда, даже при `return`.

### Встроенные типы ошибок

| тип | когда возникает |
|---|---|
| `SyntaxError` | синтаксическая ошибка, неверный JSON |
| `ReferenceError` | обращение к необъявленной переменной |
| `TypeError` | действие недопустимо для типа (`null.name`, вызов не функции) |
| `RangeError` | значение вне допустимого диапазона, слишком глубокая рекурсия |

### throw

Бросить можно что угодно, но принято использовать `Error` и его наследников:

```javascript
function setAge(age) {
  if (typeof age !== "number" || age < 0) {
    throw new RangeError("возраст должен быть неотрицательным числом");
  }
  return age;
}

try {
  setAge(-5);
} catch (e) {
  console.log(e.name, "-", e.message);
}
```

### Свои типы ошибок

```javascript
class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = "ValidationError";
  }
}

try {
  throw new ValidationError("нет имени");
} catch (e) {
  if (e instanceof ValidationError) {
    console.log("ошибка проверки:", e.message);
  } else {
    throw e;       // чужую ошибку пробрасываем дальше
  }
}
```

### Что не вызывает ошибку

JavaScript прощает многое: чтение несуществующего свойства даёт `undefined`, деление на ноль — `Infinity`, неверное число — `NaN`, выход за границы массива — `undefined`. Такие «тихие» ошибки труднее заметить, поэтому проверяйте данные явно.

### Асинхронные ошибки

Ошибки в промисах и `async`-функциях обрабатывают через `.catch(...)` или `try/catch` с `await` (подробнее в одном из следующих модулей). Обычный `try/catch` вокруг `setTimeout` их не перехватит.

### Практические советы

- не оставляйте пустой `catch`: ошибка пропадёт бесследно;
- перехватывайте только те ошибки, которые умеете обработать, остальные пробрасывайте;
- сообщение должно помогать найти причину;
- не используйте исключения для обычного управления потоком.
""",
    r"""- **Пустой `catch`.** Ошибка исчезает, программа «странно» себя ведёт.
- **Перехват слишком всего.** Прячет настоящие баги; проверяйте тип через `instanceof`.
- **`try/catch` вокруг асинхронного кода без `await`.** Не перехватит ошибку в промисе или колбэке.
- **Бросают строку вместо `Error`.** Нет стека вызовов и типа. Используйте `new Error(...)`.
- **`finally` и `return`.** Код в `finally` выполнится даже после `return`, а `return` в нём затрёт исключение.
- **Тихие ошибки.** `undefined`, `NaN` и `Infinity` не вызывают исключений: проверяйте значения.
""",
    [
        Q('Что выведет программа?', ['SyntaxError конец', 'конец', 'SyntaxError', 'Ошибка выполнения'], 0,
          '`JSON.parse` бросает `SyntaxError`, затем выполняется `finally`.',
          code='try {\n  JSON.parse("не json");\n} catch (e) {\n  process.stdout.write(e.name + " ");\n} finally {\n  process.stdout.write("конец");\n}'),
        Q('Что выведет программа?', ['TypeError', 'undefined', 'null', 'ReferenceError'], 0,
          'Обращение к свойству `null` бросает `TypeError`.',
          code='try {\n  const user = null;\n  console.log(user.name);\n} catch (e) {\n  console.log(e.name);\n}'),
        Q('Что выведет программа?', ['ReferenceError', 'TypeError', 'undefined', 'null'], 0,
          'Необъявленная переменная даёт `ReferenceError`.',
          code='try {\n  console.log(nonexistent);\n} catch (e) {\n  console.log(e.name);\n}'),
        Q('Что выведет программа?', ['RangeError - возраст должен быть неотрицательным', 'возраст должен быть неотрицательным', 'RangeError', 'undefined'], 0,
          '`name` и `message` ошибки склеиваются при выводе.',
          code='try {\n  throw new RangeError("возраст должен быть неотрицательным");\n} catch (e) {\n  console.log(e.name, "-", e.message);\n}'),
        Q('Что выведет программа?', ['finally\ntry', 'try\nfinally', 'try', 'finally'], 0,
          '`finally` выполняется до того, как значение вернётся вызывающему.',
          code='function f() {\n  try {\n    return "try";\n  } finally {\n    console.log("finally");\n  }\n}\nconsole.log(f());'),
        Q('Что выведет программа?', ['Infinity NaN', 'Ошибка Infinity', 'Infinity Ошибка', 'NaN NaN'], 0,
          'Деление на ноль и неверное число не вызывают исключений, а дают `Infinity` и `NaN`.',
          code='console.log(1 / 0, Number("abc"));'),
        Q('Что выведет программа?', ['ValidationError: нет имени', 'Error: нет имени', 'нет имени', 'ValidationError'], 0,
          'Собственный класс ошибки наследуется от `Error`; `name` задан вручную.',
          code='class ValidationError extends Error {\n  constructor(m) { super(m); this.name = "ValidationError"; }\n}\ntry {\n  throw new ValidationError("нет имени");\n} catch (e) {\n  console.log(`${e.name}: ${e.message}`);\n}'),
    ],
    videos=[],
    practice=r"""Практика этого модуля: надёжное чтение данных. Программа не должна падать на неверном вводе.""",
    problems=[('000205', 'Второй максимум: подумайте, что делать, если все числа одинаковые.')],
    task=('Безопасный калькулятор', r"""Калькулятор читает выражение вида `число операция число`. Обрабатывайте: неверное число (`Number.isNaN`), деление на ноль, неизвестную операцию (собственный класс ошибки `BadOperationError`). Используйте `try-catch-finally`.

Пришлите код и примеры «плохого» ввода."""),
    short='ошибки'))
