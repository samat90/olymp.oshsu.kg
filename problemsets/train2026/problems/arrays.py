import bisect
from collections import defaultdict
from lib import P, size, nums

PROBLEMS = []


def add(*a, **k):
    PROBLEMS.append(P(*a, **k))


# ---------- 1. pairs with given sum ----------
def gen(r, lv):
    n = size(lv, 200000)
    hi = 10 if lv < 3 else (10 ** 9 if lv % 2 else 1000)
    a = [r.randint(-hi, hi) for _ in range(n)]
    s = r.choice(a) + r.choice(a)
    return '%d %d\n%s\n' % (n, s, nums(a))


def solve(d):
    t = d.split(); n, s = int(t[0]), int(t[1]); c = defaultdict(int); res = 0
    for x in map(int, t[2:2 + n]):
        res += c[s - x]; c[x] += 1
    return str(res)


def brute(d):
    t = d.split(); n, s = int(t[0]), int(t[1]); a = list(map(int, t[2:2 + n]))
    return str(sum(1 for i in range(n) for j in range(i + 1, n) if a[i] + a[j] == s))


add('pairs_sum', 'Подарки к Нооруз', 'training', ['Массивы'], 22, """
# Подарки к Нооруз

Айгуль раскладывает подарки. У каждого подарка есть цена $a_i$ сомов (цена может быть и отрицательной: это скидочный купон). Сколько существует пар подарков с номерами $i < j$, у которых суммарная цена ровно $S$?

## Формат ввода

В первой строке записаны числа $n$ и $S$ ($2 \\le n \\le 2 \\cdot 10^5$, $|S| \\le 2 \\cdot 10^9$). Во второй строке записаны $n$ целых чисел $a_i$ ($|a_i| \\le 10^9$).

## Формат вывода

Выведите количество пар.
""", ['5 10\n3 7 5 5 5\n', '4 0\n1 -1 1 -1\n'], gen, solve, brute)


# ---------- 2. max subarray ----------
def gen(r, lv):
    n = size(lv, 200000)
    hi = 5 if lv < 3 else 10 ** 4
    bias = r.choice([0, 0, -hi // 2, hi // 3])
    a = [r.randint(-hi, hi) + bias for _ in range(n)]
    return '%d\n%s\n' % (n, nums(a))


def solve(d):
    t = list(map(int, d.split())); best = cur = -10 ** 18
    for x in t[1:1 + t[0]]:
        cur = max(x, cur + x); best = max(best, cur)
    return str(best)


def brute(d):
    t = list(map(int, d.split())); a = t[1:1 + t[0]]
    return str(max(sum(a[i:j]) for i in range(len(a)) for j in range(i + 1, len(a) + 1)))


add('best_stretch', 'Лучшая неделя чайханы', 'training', ['Массивы', 'DP'], 30, """
# Лучшая неделя чайханы

Бакыт ведёт учёт прибыли чайханы в Караколе по дням. За $i$-й день прибыль равна $a_i$ сомов (в убыточные дни — отрицательная). Найдите наибольшую суммарную прибыль за несколько **подряд идущих** дней (минимум один день).

## Формат ввода

В первой строке записано $n$ ($1 \\le n \\le 2 \\cdot 10^5$). Во второй строке — $n$ целых чисел $a_i$ ($|a_i| \\le 10^4$).

## Формат вывода

Выведите одно число — наибольшую сумму.
""", ['5\n-2 5 -1 4 -10\n', '3\n-4 -2 -7\n'], gen, solve, brute)


# ---------- 3. subarrays with sum K ----------
def gen(r, lv):
    n = size(lv, 200000)
    hi = 2 if lv < 3 else (3 if lv % 2 else 10 ** 4)
    a = [r.randint(-hi, hi) for _ in range(n)]
    i = r.randrange(n)
    k = sum(a[i:i + r.randint(1, n)])
    return '%d %d\n%s\n' % (n, k, nums(a))


def solve(d):
    t = list(map(int, d.split())); n, k = t[0], t[1]; c = defaultdict(int); c[0] = 1; s = res = 0
    for x in t[2:2 + n]:
        s += x; res += c[s - k]; c[s] += 1
    return str(res)


def brute(d):
    t = list(map(int, d.split())); n, k = t[0], t[1]; a = t[2:2 + n]
    return str(sum(1 for i in range(n) for j in range(i, n) if sum(a[i:j + 1]) == k))


add('sum_k_stretches', 'Дни с нужной выручкой', 'training', ['Массивы'], 38, """
# Дни с нужной выручкой

Эрлан торгует на Ошском базаре $n$ дней. Выручка за $i$-й день равна $a_i$ (может быть отрицательной, если пришлось возвращать деньги). Сколько существует отрезков из подряд идущих дней, в которых суммарная выручка равна ровно $K$?

## Формат ввода

В первой строке записаны $n$ и $K$ ($1 \\le n \\le 2 \\cdot 10^5$, $|K| \\le 2 \\cdot 10^9$). Во второй строке — $n$ целых чисел $a_i$ ($|a_i| \\le 10^4$).

## Формат вывода

Выведите количество подходящих отрезков.
""", ['5 3\n1 2 1 -1 3\n', '3 0\n0 0 0\n'], gen, solve, brute)


# ---------- 4. shortest segment with sum >= S ----------
def gen(r, lv):
    n = size(lv, 200000)
    hi = 6 if lv < 3 else 10 ** 4
    a = [r.randint(1, hi) for _ in range(n)]
    s = r.randint(1, sum(a) + (3 if lv % 4 == 0 else 0))
    return '%d %d\n%s\n' % (n, s, nums(a))


def solve(d):
    t = list(map(int, d.split())); n, s = t[0], t[1]; a = t[2:2 + n]
    best = n + 1; j = cur = 0
    for i in range(n):
        cur += a[i]
        while cur - a[j] >= s:
            cur -= a[j]; j += 1
        if cur >= s:
            best = min(best, i - j + 1)
    return str(best if best <= n else 0)


def brute(d):
    t = list(map(int, d.split())); n, s = t[0], t[1]; a = t[2:2 + n]
    best = 0
    for i in range(n):
        for j in range(i, n):
            if sum(a[i:j + 1]) >= s and (best == 0 or j - i + 1 < best):
                best = j - i + 1
    return str(best)


add('short_stretch', 'Кратчайший перегон каравана', 'training', ['Массивы'], 36, """
# Кратчайший перегон каравана

Караван идёт по Шёлковому пути через $n$ стоянок. Между соседними стоянками можно собрать $a_i$ кг груза. Каравану нужно набрать не менее $S$ кг, проходя **подряд идущие** участки. Найдите наименьшее количество участков, при котором это возможно, или выведите $0$, если даже весь путь не даёт $S$ кг.

## Формат ввода

В первой строке записаны $n$ и $S$ ($1 \\le n \\le 2 \\cdot 10^5$, $1 \\le S \\le 2 \\cdot 10^9$). Во второй строке — $n$ натуральных чисел $a_i$ ($1 \\le a_i \\le 10^4$).

## Формат вывода

Выведите длину кратчайшего отрезка с суммой не меньше $S$, либо $0$.
""", ['6 10\n2 3 1 2 4 3\n', '3 100\n1 2 3\n'], gen, solve, brute)


# ---------- 5. LIS ----------
def gen(r, lv):
    n = size(lv, 100000)
    hi = 6 if lv < 3 else 10 ** 9
    a = [r.randint(1, hi) for _ in range(n)]
    if lv >= 3 and lv % 3 == 0:
        a = sorted(a)
    if lv >= 3 and lv % 3 == 1:
        a = sorted(a, reverse=True)
    return '%d\n%s\n' % (n, nums(a))


def solve(d):
    t = list(map(int, d.split())); tails = []
    for x in t[1:1 + t[0]]:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return str(len(tails))


def brute(d):
    t = list(map(int, d.split())); a = t[1:1 + t[0]]; f = []
    for i in range(len(a)):
        f.append(1 + max([f[j] for j in range(i) if a[j] < a[i]], default=0))
    return str(max(f))


add('climb_lis', 'Подъёмы Тянь-Шаня', 'olympiad', ['DP', 'Двоичный поиск'], 48, """
# Подъёмы Тянь-Шаня

Альпинист записал высоты $n$ вершин хребта по порядку маршрута. Он хочет выбрать как можно больше вершин (не обязательно соседних, порядок сохраняется) так, чтобы каждая следующая была **строго выше** предыдущей. Сколько вершин можно выбрать?

## Формат ввода

В первой строке записано $n$ ($1 \\le n \\le 10^5$). Во второй строке — $n$ целых чисел $h_i$ ($1 \\le h_i \\le 10^9$).

## Формат вывода

Выведите длину наибольшей строго возрастающей подпоследовательности.
""", ['6\n5 2 8 6 3 9\n', '4\n7 7 7 7\n'], gen, solve, brute)


# ---------- 6. count less than x queries ----------
def gen(r, lv):
    n = size(lv, 200000); q = size(lv, 200000)
    hi = 8 if lv < 3 else 10 ** 9
    a = [r.randint(1, hi) for _ in range(n)]
    xs = [r.randint(0, hi + 1) for _ in range(q)]
    return '%d %d\n%s\n%s\n' % (n, q, nums(a), nums(xs))


def solve(d):
    t = list(map(int, d.split())); n, q = t[0], t[1]; a = sorted(t[2:2 + n])
    return '\n'.join(str(bisect.bisect_left(a, x)) for x in t[2 + n:2 + n + q])


def brute(d):
    t = list(map(int, d.split())); n, q = t[0], t[1]; a = t[2:2 + n]
    return '\n'.join(str(sum(1 for y in a if y < x)) for x in t[2 + n:2 + n + q])


add('count_lower', 'Дешёвые лошади', 'training', ['Двоичный поиск', 'Сортировка'], 24, """
# Дешёвые лошади

На конном рынке в Нарыне продаётся $n$ лошадей, $i$-я стоит $a_i$ сомов. К Асану по очереди подходят $q$ покупателей. Покупатель с бюджетом $x$ спрашивает: сколько лошадей **строго дешевле** $x$?

## Формат ввода

В первой строке записаны $n$ и $q$ ($1 \\le n, q \\le 2 \\cdot 10^5$). Во второй строке — $n$ цен $a_i$, в третьей — $q$ бюджетов $x_j$ ($0 \\le a_i, x_j \\le 10^9 + 1$).

## Формат вывода

Выведите $q$ чисел — по одному на строке.
""", ['5 3\n10 30 20 20 50\n20 5 100\n'], gen, solve, brute)


# ---------- 7. union length of segments ----------
def gen(r, lv):
    n = size(lv, 200000)
    hi = 12 if lv < 3 else 10 ** 9
    seg = []
    for _ in range(n):
        l = r.randint(0, hi)
        ln = r.randint(1, 4 if lv < 3 else max(1, hi // n * 3))
        seg.append((l, l + ln))
    return '%d\n%s' % (n, ''.join('%d %d\n' % s for s in seg))


def solve(d):
    t = list(map(int, d.split())); n = t[0]
    seg = sorted((t[1 + 2 * i], t[2 + 2 * i]) for i in range(n))
    total = 0; cl, cr = seg[0]
    for l, r_ in seg[1:]:
        if l > cr:
            total += cr - cl; cl, cr = l, r_
        else:
            cr = max(cr, r_)
    return str(total + cr - cl)


def brute(d):
    t = list(map(int, d.split())); n = t[0]; cells = set()
    for i in range(n):
        cells.update(range(t[1 + 2 * i], t[2 + 2 * i]))
    return str(len(cells))


add('covered_length', 'Пастбища Сон-Куля', 'training', ['Сортировка', 'Жадные'], 34, """
# Пастбища Сон-Куля

Вдоль берега озера Сон-Куль $n$ чабанов занимают участки: $i$-й занимает отрезок $[l_i, r_i)$ (в метрах от начала берега). Участки могут пересекаться. Какова общая длина берега, занятая хотя бы одним чабаном?

## Формат ввода

В первой строке записано $n$ ($1 \\le n \\le 2 \\cdot 10^5$). В следующих $n$ строках записаны $l_i$ и $r_i$ ($0 \\le l_i < r_i \\le 2 \\cdot 10^9$).

## Формат вывода

Выведите длину объединения всех отрезков.
""", ['3\n1 5\n4 8\n10 12\n', '2\n0 3\n3 6\n'], gen, solve, brute)


# ---------- 8. k-th largest ----------
def gen(r, lv):
    n = size(lv, 200000)
    hi = 8 if lv < 3 else 10 ** 9
    a = [r.randint(1, hi) for _ in range(n)]
    return '%d %d\n%s\n' % (n, r.randint(1, n), nums(a))


def solve(d):
    t = list(map(int, d.split())); n, k = t[0], t[1]
    return str(sorted(t[2:2 + n], reverse=True)[k - 1])


def brute(d):
    t = list(map(int, d.split())); n, k = t[0], t[1]; a = t[2:2 + n]
    for _ in range(k - 1):
        a.remove(max(a))
    return str(max(a))


add('kth_milk', 'Надои на ферме', 'training', ['Сортировка'], 14, """
# Надои на ферме

На ферме в Чуйской долине $n$ коров, $i$-я дала $a_i$ литров молока. Если выписать надои по убыванию (с повторами), какое число окажется на $k$-м месте?

## Формат ввода

В первой строке записаны $n$ и $k$ ($1 \\le k \\le n \\le 2 \\cdot 10^5$). Во второй строке — $n$ целых чисел $a_i$ ($1 \\le a_i \\le 10^9$).

## Формат вывода

Выведите $k$-й по величине надой (с учётом повторов).
""", ['5 2\n10 40 30 40 20\n'], gen, solve, brute)
