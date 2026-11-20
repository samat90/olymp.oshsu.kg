# flake8: noqa  (helpers come from ../_dsl.py)
MODULE = module('Объекты, Map и Set', pair(
    'Объекты, Map и Set',
    r"""### Объекты

Объект — набор пар «ключ: значение».

```javascript
const horse = {
  name: "Тулпар",
  age: 5,
  tired: false,
};

console.log(horse.name);        // Тулпар
console.log(horse["age"]);       // 5
horse.age = 6;                   // изменить
horse.color = "серый";           // добавить
delete horse.tired;              // удалить
console.log("age" in horse);     // true
```

Ключи — строки. К свойству можно обратиться через точку или через квадратные скобки; во втором случае внутри может быть переменная: `horse[key]`. У отсутствующего свойства значение `undefined`.

### Методы объекта

В объект можно положить функцию:

```javascript
const counter = {
  count: 0,
  inc() {
    this.count++;
    return this;
  },
};
counter.inc().inc();
console.log(counter.count);   // 2
```

`this` внутри метода — объект, у которого метод вызвали.

### Полезные функции

```javascript
Object.keys(horse);       // массив ключей
Object.values(horse);     // массив значений
Object.entries(horse);    // массив пар [ключ, значение]
Object.assign({}, horse); // копия (поверхностная)
const copy = { ...horse, age: 7 };   // копия с изменением
```

### Деструктуризация и сокращённая запись

```javascript
const { name, age } = horse;                  // достать поля
const x = 1, y = 2;
const point = { x, y };                        // то же, что { x: x, y: y }
const { color = "неизвестно" } = horse;        // значение по умолчанию
```

### Ссылки и копирование

Объекты, как и массивы, присваиваются по ссылке: `const b = a` не копирует. Копии `{ ...a }` и `Object.assign` **поверхностные**: вложенные объекты остаются общими. Глубокую копию делает `structuredClone(a)`.

### JSON

Формат обмена данными, похожий на запись объекта:

```javascript
const text = JSON.stringify({ name: "Тулпар", age: 5 });
console.log(text);                 // {"name":"Тулпар","age":5}
const back = JSON.parse(text);
console.log(back.name);            // Тулпар
```

### Map

`Map` — коллекция пар «ключ → значение», у которой ключами могут быть **любые** значения и которая помнит порядок добавления.

```javascript
const prices = new Map();
prices.set("курут", 120);
prices.set("кымыз", 90);
console.log(prices.get("курут"));   // 120
console.log(prices.has("мёд"));     // false
console.log(prices.size);           // 2
prices.delete("кымыз");
for (const [name, price] of prices) {
  console.log(name, price);
}
```

Подсчёт частот:

```javascript
const count = new Map();
for (const c of "мама") {
  count.set(c, (count.get(c) ?? 0) + 1);
}
```

### Set

`Set` хранит уникальные значения:

```javascript
const seen = new Set([1, 2, 2, 3, 3, 3]);
console.log(seen.size);        // 3
seen.add(4);
console.log(seen.has(2));      // true
console.log([...seen]);        // [ 1, 2, 3, 4 ]
```

Быстрый способ убрать повторы из массива: `[...new Set(arr)]`.

### Объект или Map

Для набора данных с известными полями (запись о человеке) подходит объект. Для словаря с произвольными ключами, частого добавления и удаления — `Map`.
""",
    r"""- **Ссылки вместо копий.** `const b = a` указывает на тот же объект. Копируйте через `{ ...a }` или `structuredClone`.
- **Поверхностная копия.** `{ ...a }` не копирует вложенные объекты.
- **Несуществующее свойство.** `obj.x.y` при отсутствии `x` бросает `TypeError`. Используйте `obj.x?.y`.
- **`this` потерян.** Если метод оторвать от объекта (`const f = obj.method; f()`), `this` станет другим.
- **Ключи объекта — строки.** `obj[1]` и `obj["1"]` — одно и то же.
- **Порядок ключей** числовых имён особый: они идут по возрастанию. Если порядок важен, используйте `Map`.
- **Сравнение объектов.** `{} === {}` ложно: сравниваются ссылки.
""",
    [
        Q('Что выведет программа?', ['6 серый', '5 серый', '6 undefined', '5 undefined'], 0,
          'Свойство `age` изменено, `color` добавлено.',
          code='const h = { name: "Тулпар", age: 5 };\nh.age = 6;\nh.color = "серый";\nconsole.log(h.age, h.color);'),
        Q('Что выведет программа?', ['[ \'a\', \'b\' ] [ 1, 2 ]', '[ \'a\', 1 ] [ \'b\', 2 ]', '{ a: 1, b: 2 }', 'a b 1 2'], 0,
          '`Object.keys` возвращает массив ключей, `Object.values` — массив значений.',
          code='const o = { a: 1, b: 2 };\nconsole.log(Object.keys(o), Object.values(o));'),
        Q('Что выведет программа?', ['99 99', '1 99', '99 1', '1 1'], 0,
          'Объекты присваиваются по ссылке: `b` и `a` — один и тот же объект.',
          code='const a = { x: 1 };\nconst b = a;\nb.x = 99;\nconsole.log(a.x, b.x);'),
        Q('Что выведет программа?', ['1 99', '99 99', '99 1', '1 1'], 0,
          'Копия через spread независима для простых полей.',
          code='const a = { x: 1 };\nconst b = { ...a };\nb.x = 99;\nconsole.log(a.x, b.x);'),
        Q('Что выведет программа?', ['99 99', '1 99', '99 1', '1 1'], 0,
          'Копия поверхностная: вложенный объект остался общим.',
          code='const a = { inner: { v: 1 } };\nconst b = { ...a };\nb.inner.v = 99;\nconsole.log(a.inner.v, b.inner.v);'),
        Q('Что выведет программа?', ['3 true', '6 true', '3 false', '6 false'], 0,
          '`Set` хранит только уникальные значения.',
          code='const s = new Set([1, 2, 2, 3, 3, 3]);\nconsole.log(s.size, s.has(2));'),
        Q('Что выведет программа?', ['2', '3', '0', 'undefined'], 0,
          '`Map` помнит значения по ключам; «да» встретилось дважды.',
          code='const count = new Map();\nfor (const w of ["да", "нет", "да"]) count.set(w, (count.get(w) ?? 0) + 1);\nconsole.log(count.get("да"));'),
    ],
    videos=[],
    practice=r"""Для подсчёта частот и уникальных значений используйте `Map` и `Set`.""",
    problems=[('000208', 'Сколько разных чисел в массиве: `new Set`.'),
              ('000105', 'Самый частый символ.'),
              ('000306', 'Мода массива.'),
              ('000106', 'Удалить дубликаты, сохранив порядок.')],
    task=('Частоты слов', r"""Прочитайте текст, подсчитайте слова без учёта регистра и выведите их по убыванию частоты, а при равенстве по алфавиту. Используйте `Map`, затем массив пар `[...map]` и `sort`.

Пришлите код и пример."""),
    short='объекты'))
