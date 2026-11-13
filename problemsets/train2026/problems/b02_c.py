from collections import deque, Counter
from lib import prob, size, nums, ints


def N(lv, big, lo=1):
    return max(lo, size(lv, big))


def hi_of(r, lv, big):
    return 4 if lv < 3 else r.choice([6, 100, 10 ** 4, big])


def rl(r, n, lo, hi):
    return [r.randint(lo, hi) for _ in range(n)]


# 2
@prob('b02_c_closest_three', 'Три мешка муки', 'training', ['Массивы', 'Сортировка'], 38,
      r"На складе в Нарыне $n$ мешков, в $i$-м лежит $a_i$ кг муки. Айгуль выбирает три разных мешка так, чтобы их общий вес был как можно ближе к заказу $T$. Выведите наименьшее возможное значение $|a_i+a_j+a_k-T|$.",
      r"В первой строке $n$ и $T$ ($3 \le n \le 1000$, $|T| \le 3\cdot 10^9$). Во второй — $n$ целых чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Одно число.", ['4 1\n-1 2 1 -4\n'])
class _:
    def gen(r, lv):
        n = N(lv, 1000, 3)
        hi = hi_of(r, lv, 10 ** 9)
        a = rl(r, n, -hi, hi)
        T = r.randint(-3 * hi, 3 * hi)
        return '%d %d\n%s\n' % (n, T, nums(a))

    def solve(d):
        t = ints(d); n, T = t[0], t[1]; a = sorted(t[2:2 + n]); best = 10 ** 18
        for i in range(n - 2):
            l, rr = i + 1, n - 1
            while l < rr:
                s = a[i] + a[l] + a[rr]
                best = min(best, abs(s - T))
                if s < T: l += 1
                elif s > T: rr -= 1
                else: return '0'
        return str(best)

    def brute(d):
        t = ints(d); n, T = t[0], t[1]; a = t[2:2 + n]
        return str(min(abs(a[i] + a[j] + a[k] - T) for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n)))


# 3
@prob('b02_c_light_triples', 'Лёгкие тройки ягнят', 'training', ['Массивы', 'Сортировка'], 40,
      r"У чабана $n$ ягнят, вес $i$-го равен $a_i$. Нурлан хочет посадить в повозку трёх ягнят, суммарный вес которых строго меньше $T$. Сколько существует способов выбрать тройку (способы различаются номерами ягнят)?",
      r"В первой строке $n$ и $T$ ($3 \le n \le 1000$, $|T| \le 3\cdot 10^9$). Во второй — $n$ целых чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Количество троек.", ['5 4\n1 1 2 3 0\n'])
class _:
    def gen(r, lv):
        n = N(lv, 1000, 3)
        hi = hi_of(r, lv, 10 ** 9)
        a = rl(r, n, -hi, hi)
        return '%d %d\n%s\n' % (n, r.randint(-hi, hi), nums(a))

    def solve(d):
        t = ints(d); n, T = t[0], t[1]; a = sorted(t[2:2 + n]); res = 0
        for i in range(n - 2):
            l, rr = i + 1, n - 1
            while l < rr:
                if a[i] + a[l] + a[rr] < T:
                    res += rr - l; l += 1
                else:
                    rr -= 1
        return str(res)

    def brute(d):
        t = ints(d); n, T = t[0], t[1]; a = t[2:2 + n]
        return str(sum(1 for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n) if a[i] + a[j] + a[k] < T))


# 4
@prob('b02_c_two_cups', 'Не больше двух пиал', 'training', ['Массивы'], 10,
      r"Бакыт расставил пиалы на полке по неубыванию размера $a_i$. Чтобы не было тесно, он оставляет от каждого размера не более двух пиал (порядок сохраняется). Выведите размеры оставшихся пиал.",
      r"В первой строке $n$ ($1 \le n \le 2\cdot 10^5$). Во второй — $n$ целых чисел $a_i$ в порядке неубывания ($|a_i| \le 10^9$).",
      r"Размеры оставшихся пиал через пробел.", ['7\n1 1 1 2 3 3 3\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        hi = r.choice([2, 5, n, 10 ** 9]) if lv >= 3 else 3
        return '%d\n%s\n' % (n, nums(sorted(rl(r, n, -hi, hi))))

    def solve(d):
        t = ints(d); a = t[1:1 + t[0]]; k = 0; res = []
        for x in a:
            if k < 2 or res[k - 2] != x:
                res.append(x); k += 1
        return nums(res)

    def brute(d):
        t = ints(d); a = t[1:1 + t[0]]; c = Counter(); res = []
        for x in a:
            c[x] += 1
            if c[x] <= 2: res.append(x)
        return nums(res)


# 5
@prob('b02_c_merge_caravans', 'Слияние двух караванов', 'training', ['Массивы', 'Сортировка'], 14,
      r"Два каравана идут в Чолпон-Ату. В первом $n$ верблюдов с номерами $a_i$, во втором $m$ верблюдов с номерами $b_j$; в каждом списке номера записаны по возрастанию. Составьте общий список всех различных номеров по возрастанию.",
      r"В первой строке $n$ и $m$ ($1 \le n, m \le 2\cdot 10^5$). Во второй — $a_i$ по возрастанию, в третьей — $b_j$ по возрастанию ($|a_i|,|b_j| \le 10^9$).",
      r"Номера через пробел.", ['3 3\n1 4 7\n2 4 9\n'])
class _:
    def gen(r, lv):
        n, m = N(lv, 2 * 10 ** 5), N(lv, 2 * 10 ** 5)
        hi = 20 if lv < 3 else r.choice([n + m, 10 ** 9])
        a = sorted(r.sample(range(-hi, hi + 1), min(n, 2 * hi + 1)))
        b = sorted(r.sample(range(-hi, hi + 1), min(m, 2 * hi + 1)))
        return '%d %d\n%s\n%s\n' % (len(a), len(b), nums(a), nums(b))

    def solve(d):
        t = ints(d); n, m = t[0], t[1]; a = t[2:2 + n]; b = t[2 + n:2 + n + m]
        i = j = 0; res = []
        while i < n or j < m:
            if j >= m or (i < n and a[i] <= b[j]): x = a[i]; i += 1
            else: x = b[j]; j += 1
            if not res or res[-1] != x: res.append(x)
        return nums(res)

    def brute(d):
        t = ints(d); n, m = t[0], t[1]
        return nums(sorted(set(t[2:2 + n + m])))


# 6
@prob('b02_c_small_product', 'Скромный урожай', 'training', ['Массивы'], 33,
      r"В $i$-й день Айгуль собирает $a_i$ кг абрикосов. Назовём отрезок подряд идущих дней скромным, если произведение сборов за эти дни строго меньше $K$. Сколько всего скромных отрезков?",
      r"В первой строке $n$ и $K$ ($1 \le n \le 2\cdot 10^5$, $1 \le K \le 10^9$). Во второй — $n$ целых чисел $a_i$ ($1 \le a_i \le 10^4$).",
      r"Количество отрезков.", ['4 100\n10 5 2 6\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        hi = r.choice([2, 3, 10, 100, 10 ** 4]) if lv >= 3 else 4
        K = r.randint(1, 30) if lv < 3 else r.choice([r.randint(1, 10 ** 9), 10 ** 9, hi ** 2, hi ** 3])
        K = max(1, min(K, 10 ** 9))
        return '%d %d\n%s\n' % (n, K, nums(rl(r, n, 1, hi)))

    def solve(d):
        t = ints(d); n, K = t[0], t[1]; a = t[2:2 + n]; l = 0; p = 1; res = 0
        for rr in range(n):
            p *= a[rr]
            while l <= rr and p >= K:
                p //= a[l]; l += 1
            res += rr - l + 1
        return str(res)

    def brute(d):
        t = ints(d); n, K = t[0], t[1]; a = t[2:2 + n]; res = 0
        for i in range(n):
            p = 1
            for j in range(i, n):
                p *= a[j]
                if p < K: res += 1
        return str(res)


# 7
@prob('b02_c_k_kinds', 'Не более K сортов', 'training', ['Массивы'], 28,
      r"На базаре в Оше $n$ мешков с зерном, в $i$-м лежит сорт $a_i$. Чолпон берёт подряд идущие мешки, но не хочет возить больше $K$ разных сортов. Какое наибольшее число мешков подряд можно взять?",
      r"В первой строке $n$ и $K$ ($1 \le K \le n \le 2\cdot 10^5$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"Одно число.", ['6 2\n1 2 1 3 3 1\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        v = r.choice([2, 3, 10, n, 10 ** 9]) if lv >= 3 else 3
        return '%d %d\n%s\n' % (n, r.randint(1, min(n, r.choice([1, 2, 5, n]))), nums(rl(r, n, 1, v)))

    def solve(d):
        t = ints(d); n, K = t[0], t[1]; a = t[2:2 + n]; c = {}; l = best = 0
        for rr in range(n):
            c[a[rr]] = c.get(a[rr], 0) + 1
            while len(c) > K:
                c[a[l]] -= 1
                if not c[a[l]]: del c[a[l]]
                l += 1
            best = max(best, rr - l + 1)
        return str(best)

    def brute(d):
        t = ints(d); n, K = t[0], t[1]; a = t[2:2 + n]
        return str(max(j - i + 1 for i in range(n) for j in range(i, n) if len(set(a[i:j + 1])) <= K))


# 8
@prob('b02_c_even_stretch', 'Ровная полоса пастбища', 'training', ['Массивы', 'Структуры данных'], 42,
      r"Высоты участков вдоль склона у Нарына равны $a_1,\dots,a_n$. Нурлан ищет самую длинную полосу подряд идущих участков, где разница между самым высоким и самым низким не превышает $D$. Выведите длину этой полосы.",
      r"В первой строке $n$ и $D$ ($1 \le n \le 2\cdot 10^5$, $0 \le D \le 10^9$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^9$).",
      r"Одно число.", ['6 3\n8 2 4 7 5 6\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        hi = hi_of(r, lv, 10 ** 9)
        a = rl(r, n, 0, hi)
        if lv >= 3 and r.random() < 0.5:
            x = r.randint(0, hi); a = [min(hi, max(0, x + r.randint(-5, 5))) for _ in range(n)]
        return '%d %d\n%s\n' % (n, r.randint(0, max(1, hi // r.choice([1, 2, 10]))), nums(a))

    def solve(d):
        t = ints(d); n, D = t[0], t[1]; a = t[2:2 + n]
        mx, mn = deque(), deque(); l = best = 0
        for i in range(n):
            while mx and a[mx[-1]] <= a[i]: mx.pop()
            mx.append(i)
            while mn and a[mn[-1]] >= a[i]: mn.pop()
            mn.append(i)
            while a[mx[0]] - a[mn[0]] > D:
                l += 1
                if mx[0] < l: mx.popleft()
                if mn[0] < l: mn.popleft()
            best = max(best, i - l + 1)
        return str(best)

    def brute(d):
        t = ints(d); n, D = t[0], t[1]; a = t[2:2 + n]
        return str(max(j - i + 1 for i in range(n) for j in range(i, n) if max(a[i:j + 1]) - min(a[i:j + 1]) <= D))


# 10
@prob('b02_c_three_ribbons', 'Три цвета лент', 'training', ['Массивы', 'Жадные'], 36,
      r"Лента из $n$ лоскутов раскрашена цветами 0, 1 и 2. Айгуль хочет расположить цвета по неубыванию, меняя местами любые два лоскута за одну операцию. Какое наименьшее число обменов потребуется?",
      r"В первой строке $n$ ($1 \le n \le 2\cdot 10^5$). Во второй — $n$ чисел $c_i \in \{0,1,2\}$.",
      r"Одно число.", ['6\n2 0 1 2 1 0\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        w = r.choice([[1, 1, 1], [5, 1, 1], [1, 5, 1], [1, 1, 5], [1, 0, 1]])
        return '%d\n%s\n' % (n, nums(r.choices([0, 1, 2], w, k=n)))

    def solve(d):
        t = ints(d); n = t[0]; c = t[1:1 + n]
        cnt = [c.count(0), c.count(1), c.count(2)]
        pos = [0, cnt[0], cnt[0] + cnt[1], n]
        m = [[0] * 3 for _ in range(3)]
        for i in range(3):
            for x in c[pos[i]:pos[i + 1]]: m[i][x] += 1
        res = 0
        for i in range(3):
            for j in range(i + 1, 3):
                k = min(m[i][j], m[j][i]); res += k; m[i][j] -= k; m[j][i] -= k
        rest = sum(m[i][j] for i in range(3) for j in range(3) if i != j)
        return str(res + rest // 3 * 2)

    def brute(d):
        t = ints(d); n = t[0]; s = tuple(t[1:1 + n]); goal = tuple(sorted(s))
        dist = {s: 0}; q = deque([s])
        while q:
            u = q.popleft()
            if u == goal: return str(dist[u])
            for i in range(n):
                for j in range(i + 1, n):
                    if u[i] != u[j]:
                        v = list(u); v[i], v[j] = v[j], v[i]; v = tuple(v)
                        if v not in dist: dist[v] = dist[u] + 1; q.append(v)


# 11
@prob('b02_c_sign_repaint', 'Подновить вывеску', 'training', ['Строки'], 34,
      r"На вывеске чайханы в Оше написана строка из заглавных латинских букв. Бакыт может перекрасить не более $K$ букв в любые другие. Какую наибольшую длину может иметь отрезок подряд из одинаковых букв после перекраски?",
      r"В первой строке $n$ и $K$ ($1 \le n \le 2\cdot 10^5$, $0 \le K \le n$). Во второй — строка длины $n$ из букв A–Z.",
      r"Одно число.", ['7 2\nABAABBA\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        al = 'ABC' if lv < 3 else 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[:r.choice([2, 3, 5, 26])]
        s = ''.join(r.choice(al) for _ in range(n))
        return '%d %d\n%s\n' % (n, r.randint(0, min(n, r.choice([0, 1, 3, n]))), s)

    def solve(d):
        t = d.split(); n, K = int(t[0]), int(t[1]); s = t[2]; best = 0
        for ch in set(s):
            l = bad = 0
            for i in range(n):
                bad += s[i] != ch
                while bad > K:
                    bad -= s[l] != ch; l += 1
                best = max(best, i - l + 1)
        return str(best)

    def brute(d):
        t = d.split(); n, K = int(t[0]), int(t[1]); s = t[2]; best = 0
        for i in range(n):
            for j in range(i, n):
                w = s[i:j + 1]
                if len(w) - max(Counter(w).values()) <= K: best = max(best, j - i + 1)
        return str(best)


# 12
@prob('b02_c_full_beads', 'Полный набор бусин', 'training', ['Строки'], 37,
      r"Нить бус Айгуль задана строкой из строчных латинских букв, каждая буква — цвет бусины. Найдите длину самого короткого отрезка подряд идущих бусин, в котором встречаются все цвета, имеющиеся на всей нити.",
      r"Одна строка $s$ ($1 \le |s| \le 2\cdot 10^5$) из букв a–z.",
      r"Одно число.", ['abcabbcaab\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        k = r.choice([1, 2, 3, 5, 10, 26]) if lv >= 3 else 3
        al = 'abcdefghijklmnopqrstuvwxyz'[:k]
        return ''.join(r.choice(al) for _ in range(n)) + '\n'

    def solve(d):
        s = d.split()[0]; need = len(set(s)); c = {}; l = 0; best = len(s)
        for i, ch in enumerate(s):
            c[ch] = c.get(ch, 0) + 1
            while len(c) == need:
                best = min(best, i - l + 1)
                c[s[l]] -= 1
                if not c[s[l]]: del c[s[l]]
                l += 1
        return str(best)

    def brute(d):
        s = d.split()[0]; k = len(set(s)); n = len(s)
        return str(min(j - i + 1 for i in range(n) for j in range(i, n) if len(set(s[i:j + 1])) == k))


# 13
@prob('b02_c_budget_road', 'Бюджет на дорогу', 'training', ['Массивы'], 20,
      r"Участок трассы Бишкек — Нарын разбит на $n$ отрезков, ремонт $i$-го стоит $a_i$ сомов. На ремонт выделено $S$ сомов. Какое наибольшее число подряд идущих отрезков можно отремонтировать на эти деньги? Если не хватает даже на один, выведите 0.",
      r"В первой строке $n$ и $S$ ($1 \le n \le 2\cdot 10^5$, $0 \le S \le 10^{14}$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^9$).",
      r"Одно число.", ['5 7\n4 2 3 1 5\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        hi = hi_of(r, lv, 10 ** 9)
        a = rl(r, n, 0, hi)
        S = r.randint(0, min(10 ** 14, sum(a) + 1)) if r.random() < 0.9 else r.randint(0, 10 ** 14)
        return '%d %d\n%s\n' % (n, S, nums(a))

    def solve(d):
        t = ints(d); n, S = t[0], t[1]; a = t[2:2 + n]; l = s = best = 0
        for i in range(n):
            s += a[i]
            while s > S:
                s -= a[l]; l += 1
            best = max(best, i - l + 1)
        return str(best)

    def brute(d):
        t = ints(d); n, S = t[0], t[1]; a = t[2:2 + n]
        return str(max([0] + [j - i + 1 for i in range(n) for j in range(i, n) if sum(a[i:j + 1]) <= S]))


# 14
@prob('b02_c_boat_pairs', 'Пары в одну лодку', 'training', ['Массивы', 'Сортировка', 'Жадные'], 30,
      r"Девушки приехали на Иссык-Куль, вес $i$-й равен $w_i$. Лодка выдерживает не более $W$ кг и берёт не более двух человек. Какое наименьшее число лодок нужно, чтобы перевезти всех? Гарантируется, что $w_i \le W$.",
      r"В первой строке $n$ и $W$ ($1 \le n \le 2\cdot 10^5$, $1 \le W \le 10^9$). Во второй — $n$ чисел $w_i$ ($1 \le w_i \le W$).",
      r"Одно число.", ['5 100\n50 80 30 70 20\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        W = r.randint(1, 12) if lv < 3 else r.choice([10, 100, 10 ** 9])
        lo = r.choice([1, max(1, W // 3)])
        return '%d %d\n%s\n' % (n, W, nums(rl(r, n, lo, W)))

    def solve(d):
        t = ints(d); n, W = t[0], t[1]; a = sorted(t[2:2 + n]); l, rr, res = 0, n - 1, 0
        while l <= rr:
            if l < rr and a[l] + a[rr] <= W: l += 1
            rr -= 1; res += 1
        return str(res)

    def brute(d):
        t = ints(d); n, W = t[0], t[1]; a = t[2:2 + n]
        best = [n]

        def go(mask, cnt):
            if cnt >= best[0]: return
            if mask == (1 << n) - 1: best[0] = cnt; return
            i = 0
            while mask >> i & 1: i += 1
            go(mask | 1 << i, cnt + 1)
            for j in range(i + 1, n):
                if not mask >> j & 1 and a[i] + a[j] <= W: go(mask | 1 << i | 1 << j, cnt + 1)
        go(0, 0)
        return str(best[0])


# 15
@prob('b02_c_near_pair', 'Ближайшая пара подарков', 'training', ['Массивы', 'Сортировка'], 24,
      r"На прилавке $n$ сувениров, цена $i$-го равна $a_i$. Нурлан выбирает два разных сувенира, чтобы их общая цена была как можно ближе к его бюджету $T$. Выведите наименьшее возможное значение $|a_i+a_j-T|$.",
      r"В первой строке $n$ и $T$ ($2 \le n \le 2\cdot 10^5$, $|T| \le 2\cdot 10^9$). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Одно число.", ['4 10\n1 4 9 20\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5, 2)
        hi = hi_of(r, lv, 10 ** 9)
        return '%d %d\n%s\n' % (n, r.randint(-2 * hi, 2 * hi), nums(rl(r, n, -hi, hi)))

    def solve(d):
        t = ints(d); n, T = t[0], t[1]; a = sorted(t[2:2 + n]); l, rr, best = 0, n - 1, 10 ** 18
        while l < rr:
            s = a[l] + a[rr]; best = min(best, abs(s - T))
            if s < T: l += 1
            else: rr -= 1
        return str(best)

    def brute(d):
        t = ints(d); n, T = t[0], t[1]; a = t[2:2 + n]
        return str(min(abs(a[i] + a[j] - T) for i in range(n) for j in range(i + 1, n)))


# 17
@prob('b02_c_income_corridor', 'Коридор выручки', 'training', ['Массивы'], 48,
      r"Выручка лавки Бакыта в $i$-й день равна $a_i$ сомов. Сколько существует отрезков подряд идущих дней, суммарная выручка за которые лежит в пределах от $L$ до $R$ включительно?",
      r"В первой строке $n$, $L$ и $R$ ($1 \le n \le 2\cdot 10^5$, $0 \le L \le R \le 10^{14}$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^9$).",
      r"Количество отрезков.", ['4 3 5\n1 2 0 4\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        hi = hi_of(r, lv, 10 ** 9)
        a = rl(r, n, 0, hi)
        tot = sum(a)
        L = r.randint(0, tot // r.choice([1, 2, 50, 1000]) + 1)
        R = min(10 ** 14, L + r.randint(0, tot // r.choice([1, 5, 100]) + 1))
        L = min(L, R)
        return '%d %d %d\n%s\n' % (n, L, R, nums(a))

    def solve(d):
        t = ints(d); n, L, R = t[0], t[1], t[2]; a = t[3:3 + n]

        def most(X):
            if X < 0: return 0
            l = s = res = 0
            for i in range(n):
                s += a[i]
                while s > X:
                    s -= a[l]; l += 1
                res += i - l + 1
            return res
        return str(most(R) - most(L - 1))

    def brute(d):
        t = ints(d); n, L, R = t[0], t[1], t[2]; a = t[3:3 + n]
        return str(sum(1 for i in range(n) for j in range(i, n) if L <= sum(a[i:j + 1]) <= R))


# 18
@prob('b02_c_sort_patch', 'Сбитый участок', 'training', ['Массивы', 'Сортировка'], 32,
      r"Ряд из $n$ юрт пронумерован числами $a_i$ и должен идти по неубыванию, но порядок нарушен. Айгуль хочет выбрать один участок подряд идущих юрт и расставить их внутри участка по неубыванию так, чтобы весь ряд стал упорядоченным. Какова наименьшая возможная длина такого участка? Если ряд уже упорядочен, выведите 0.",
      r"В первой строке $n$ ($1 \le n \le 2\cdot 10^5$). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Одно число.", ['7\n1 2 6 4 5 8 9\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        hi = r.choice([2, 5, n, 10 ** 9]) if lv >= 3 else 3
        a = sorted(rl(r, n, -hi, hi))
        for _ in range(r.choice([0, 1, 1, 2, 3])):
            i = r.randrange(n); j = r.randrange(n)
            if r.random() < 0.5: a[i], a[j] = a[j], a[i]
            else: a[i] = r.randint(-hi, hi)
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; end = -1; mx = a[0]
        for i in range(n):
            if a[i] < mx: end = i
            else: mx = a[i]
        if end < 0: return '0'
        start = 0; mn = a[-1]
        for i in range(n - 1, -1, -1):
            if a[i] > mn: start = i
            else: mn = a[i]
        return str(end - start + 1)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; s = sorted(a)
        df = [i for i in range(n) if a[i] != s[i]]
        return str(df[-1] - df[0] + 1 if df else 0)


# 19
@prob('b02_c_common_horseshoes', 'Общие подковы', 'training', ['Массивы'], 18,
      r"У кузнеца Нурлана $n$ подков с размерами $a_i$, у кузнеца Бакыта — $m$ подков с размерами $b_j$; оба списка записаны по неубыванию. Они хотят составить как можно больше пар «подкова Нурлана — подкова Бакыта» одного размера, используя каждую подкову не более одного раза. Сколько пар получится?",
      r"В первой строке $n$ и $m$ ($1 \le n, m \le 2\cdot 10^5$). Во второй и третьей строках — списки $a_i$ и $b_j$ по неубыванию ($1 \le a_i, b_j \le 10^9$).",
      r"Одно число.", ['5 4\n1 2 2 2 5\n2 2 3 5\n'])
class _:
    def gen(r, lv):
        n, m = N(lv, 2 * 10 ** 5), N(lv, 2 * 10 ** 5)
        hi = r.choice([3, 10, n, 10 ** 9]) if lv >= 3 else 4
        a = sorted(rl(r, n, 1, hi)); b = sorted(rl(r, m, 1, hi))
        return '%d %d\n%s\n%s\n' % (n, m, nums(a), nums(b))

    def solve(d):
        t = ints(d); n, m = t[0], t[1]; a = t[2:2 + n]; b = t[2 + n:2 + n + m]; i = j = res = 0
        while i < n and j < m:
            if a[i] < b[j]: i += 1
            elif a[i] > b[j]: j += 1
            else: res += 1; i += 1; j += 1
        return str(res)

    def brute(d):
        t = ints(d); n, m = t[0], t[1]; a = Counter(t[2:2 + n]); b = Counter(t[2 + n:2 + n + m])
        return str(sum(min(a[x], b[x]) for x in a))


# 20
@prob('b02_c_squared_frost', 'Квадраты мороза', 'training', ['Массивы', 'Сортировка'], 15,
      r"Температуры в Нарыне за $n$ дней записаны по неубыванию: $t_1 \le t_2 \le \dots \le t_n$ (есть и отрицательные). Метеоролог возводит каждое значение в квадрат. Выведите все квадраты по неубыванию.",
      r"В первой строке $n$ ($1 \le n \le 2\cdot 10^5$). Во второй — $n$ целых чисел $t_i$ по неубыванию ($|t_i| \le 10^4$).",
      r"$n$ чисел через пробел.", ['5\n-4 -1 0 3 10\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        hi = r.choice([5, 100, 10 ** 4]) if lv >= 3 else 4
        lo = r.choice([-hi, -hi, 0, -1])
        return '%d\n%s\n' % (n, nums(sorted(rl(r, n, lo, hi))))

    def solve(d):
        t = ints(d); a = t[1:1 + t[0]]; l, rr = 0, len(a) - 1; res = []
        while l <= rr:
            if abs(a[l]) > abs(a[rr]): res.append(a[l] * a[l]); l += 1
            else: res.append(a[rr] * a[rr]); rr -= 1
        return nums(res[::-1])

    def brute(d):
        t = ints(d); return nums(sorted(x * x for x in t[1:1 + t[0]]))


# 21
@prob('b02_c_almost_mirror', 'Почти зеркало', 'training', ['Строки'], 26,
      r"Манасчи записал название песни строкой из строчных латинских букв. Можно ли вычеркнуть не более одной буквы так, чтобы получилась строка, читающаяся одинаково слева направо и справа налево?",
      r"Одна строка $s$ ($1 \le |s| \le 2\cdot 10^5$) из букв a–z.",
      r"YES или NO.", ['abcdcbea\n', 'abc\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        k = r.choice([2, 3, 26]) if lv >= 3 else 2
        al = 'abcdefghijklmnopqrstuvwxyz'[:k]
        h = [r.choice(al) for _ in range(n // 2)]
        s = h + ([r.choice(al)] if n % 2 else []) + h[::-1]
        c = r.randrange(4)
        if c == 1 and s: s[r.randrange(len(s))] = r.choice(al)
        elif c == 2 and s: s.insert(r.randrange(len(s) + 1), r.choice(al))
        elif c == 3 and len(s) > 3:
            s[r.randrange(len(s))] = r.choice(al); s[r.randrange(len(s))] = r.choice(al)
        return ''.join(s[:2 * 10 ** 5]) + '\n'

    def solve(d):
        s = d.split()[0]

        def pal(i, j):
            while i < j:
                if s[i] != s[j]: return False
                i += 1; j -= 1
            return True
        i, j = 0, len(s) - 1
        while i < j:
            if s[i] != s[j]:
                return 'YES' if pal(i + 1, j) or pal(i, j - 1) else 'NO'
            i += 1; j -= 1
        return 'YES'

    def brute(d):
        s = d.split()[0]
        ok = s == s[::-1] or any((s[:i] + s[i + 1:]) == (s[:i] + s[i + 1:])[::-1] for i in range(len(s)))
        return 'YES' if ok else 'NO'


# 22
@prob('b02_c_mountain_run', 'Горный хребет', 'training', ['Массивы'], 22,
      r"Высоты вершин вдоль хребта Ала-Тоо равны $h_1,\dots,h_n$. Участок подряд идущих вершин назовём горкой, если высоты в нём сначала строго растут, потом строго убывают, причём обе части непустые (то есть вершин не менее трёх). Найдите длину самой длинной горки или 0, если горок нет.",
      r"В первой строке $n$ ($1 \le n \le 2\cdot 10^5$). Во второй — $n$ чисел $h_i$ ($0 \le h_i \le 10^9$).",
      r"Одно число.", ['8\n2 1 4 7 3 2 5 6\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        hi = r.choice([2, 5, 100, 10 ** 9]) if lv >= 3 else 4
        if lv >= 5 and r.random() < 0.6:
            a = []
            while len(a) < n:
                m = r.randint(2, max(2, n // r.randint(1, 4)))
                u = sorted(r.sample(range(0, hi + 1), min(m, hi + 1)))
                a += u + u[-2::-1][:r.randint(0, len(u))]
            a = a[:n]
        else:
            a = rl(r, n, 0, hi)
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; best = 0; i = 0
        while i < n - 1:
            j = i
            while j + 1 < n and a[j] < a[j + 1]: j += 1
            if j == i:
                i += 1; continue
            k = j
            while k + 1 < n and a[k] > a[k + 1]: k += 1
            if k > j:
                best = max(best, k - i + 1); i = k
            else:
                i = j
        return str(best)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; best = 0
        for i in range(n):
            for j in range(i + 2, n):
                for p in range(i + 1, j):
                    if all(a[x] < a[x + 1] for x in range(i, p)) and all(a[x] > a[x + 1] for x in range(p, j)):
                        best = max(best, j - i + 1)
        return str(best)


# 25
@prob('b02_c_cheap_pairs', 'Недорогие пары', 'training', ['Массивы', 'Сортировка', 'Двоичный поиск'], 31,
      r"На ярмарке в Чолпон-Ате $n$ шапок, цена $i$-й равна $a_i$ сомов. Айгуль берёт две разные шапки в подарок и готова заплатить за обе не более $X$ сомов. Сколько существует пар шапок $i<j$ с $a_i+a_j \le X$?",
      r"В первой строке $n$ и $X$ ($2 \le n \le 2\cdot 10^5$, $0 \le X \le 2\cdot 10^9$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^9$).",
      r"Количество пар.", ['4 6\n1 5 3 4\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5, 2)
        hi = hi_of(r, lv, 10 ** 9)
        return '%d %d\n%s\n' % (n, r.randint(0, 2 * hi), nums(rl(r, n, 0, hi)))

    def solve(d):
        t = ints(d); n, X = t[0], t[1]; a = sorted(t[2:2 + n]); l, rr, res = 0, n - 1, 0
        while l < rr:
            if a[l] + a[rr] <= X: res += rr - l; l += 1
            else: rr -= 1
        return str(res)

    def brute(d):
        t = ints(d); n, X = t[0], t[1]; a = t[2:2 + n]
        return str(sum(1 for i in range(n) for j in range(i + 1, n) if a[i] + a[j] <= X))



# 1
@prob('b02_c_ramp_posts', 'Склон между опорами', 'training', ['Массивы', 'Жадные'], 40,
      r"Вдоль канала в Оше стоят $n$ опор, высота $i$-й равна $h_i$. Бакыт хочет проложить жёлоб от опоры $i$ к опоре $j$, где $i<j$ и $h_i \le h_j$. Найдите наибольшее возможное значение $j-i$. Если подходящих пар нет, выведите 0.",
      r"В первой строке $n$ ($1 \le n \le 2\cdot 10^5$). Во второй — $n$ целых чисел $h_i$ ($0 \le h_i \le 10^9$).",
      r"Одно число.", ['6\n6 0 8 2 1 5\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        hi = hi_of(r, lv, 10 ** 9)
        a = rl(r, n, 0, hi)
        if lv >= 4 and r.random() < 0.4: a.sort(reverse=True)
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        pm = [a[0]] * n
        for i in range(1, n): pm[i] = min(pm[i - 1], a[i])
        sm = [a[-1]] * n
        for i in range(n - 2, -1, -1): sm[i] = max(sm[i + 1], a[i])
        i = j = best = 0
        while j < n:
            if pm[i] <= sm[j]:
                best = max(best, j - i); j += 1
            else:
                i += 1
        return str(best)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        return str(max([0] + [j - i for i in range(n) for j in range(i + 1, n) if a[i] <= a[j]]))


# 9
@prob('b02_c_calm_window', 'Тихий перевал', 'training', ['Массивы', 'Структуры данных'], 46,
      r"Метеостанция на перевале записала температуру $a_i$ в $i$-й день. Для окна из $k$ подряд идущих дней размахом называется разность между наибольшей и наименьшей температурой в окне. Найдите наименьший размах среди всех окон.",
      r"В первой строке $n$ и $k$ ($1 \le k \le n \le 2\cdot 10^5$). Во второй — $n$ целых чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Одно число.", ['6 3\n5 1 4 7 8 3\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        hi = hi_of(r, lv, 10 ** 9)
        a = rl(r, n, -hi, hi)
        return '%d %d\n%s\n' % (n, r.randint(1, n) if lv < 3 or r.random() < 0.5 else r.randint(1, min(n, 100)), nums(a))

    def solve(d):
        t = ints(d); n, k = t[0], t[1]; a = t[2:2 + n]; mx, mn = deque(), deque(); best = 10 ** 18
        for i in range(n):
            while mx and a[mx[-1]] <= a[i]: mx.pop()
            mx.append(i)
            while mn and a[mn[-1]] >= a[i]: mn.pop()
            mn.append(i)
            if mx[0] <= i - k: mx.popleft()
            if mn[0] <= i - k: mn.popleft()
            if i >= k - 1: best = min(best, a[mx[0]] - a[mn[0]])
        return str(best)

    def brute(d):
        t = ints(d); n, k = t[0], t[1]; a = t[2:2 + n]
        return str(min(max(a[i:i + k]) - min(a[i:i + k]) for i in range(n - k + 1)))


# 16
@prob('b02_c_gold_period', 'Выручка за период', 'training', ['Массивы', 'Структуры данных'], 58,
      r"Выручка лавки Бакыта в $i$-й день равна $a_i$ сомов (бывают убытки). Он выбирает период из подряд идущих дней длиной от $L$ до $R$ включительно. Какую наибольшую суммарную выручку можно получить?",
      r"В первой строке $n$, $L$ и $R$ ($1 \le L \le R \le n \le 2\cdot 10^5$). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Одно число.", ['6 2 3\n-1 5 -2 4 -6 3\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        hi = hi_of(r, lv, 10 ** 9)
        L = r.randint(1, n); R = r.randint(L, n)
        if lv >= 3 and r.random() < 0.5: R = min(n, L + r.randint(0, 50))
        bias = r.choice([0, 0, -hi // 3])
        return '%d %d %d\n%s\n' % (n, L, R, nums([max(-hi, x + bias) for x in rl(r, n, -hi, hi)]))

    def solve(d):
        t = ints(d); n, L, R = t[0], t[1], t[2]; a = t[3:3 + n]
        p = [0] * (n + 1)
        for i in range(n): p[i + 1] = p[i] + a[i]
        q = deque(); best = -10 ** 18
        for j in range(L, n + 1):
            i = j - L
            while q and p[q[-1]] >= p[i]: q.pop()
            q.append(i)
            while q[0] < j - R: q.popleft()
            best = max(best, p[j] - p[q[0]])
        return str(best)

    def brute(d):
        t = ints(d); n, L, R = t[0], t[1], t[2]; a = t[3:3 + n]
        return str(max(sum(a[i:j]) for i in range(n) for j in range(i + L, min(n, i + R) + 1)))


# 24
@prob('b02_c_odd_chests', 'Сундуки с нечётным грузом', 'training', ['Массивы'], 38,
      r"На складе в Нарыне лежат $n$ сундуков, в $i$-м находится $a_i$ слитков. Назовём «тяжёлыми» сундуки с нечётным числом слитков. Сколько существует отрезков подряд идущих сундуков, содержащих ровно $K$ тяжёлых?",
      r"В первой строке $n$ и $K$ ($1 \le n \le 2\cdot 10^5$, $0 \le K \le n$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"Одно число.", ['5 2\n1 2 3 4 5\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        w = r.choice([1, 3, 10])
        a = [2 * r.randint(1, 10 ** 9 // 2 - 1) + (r.randrange(w) == 0) for _ in range(n)]
        return '%d %d\n%s\n' % (n, r.randint(0, min(n, r.choice([0, 1, 2, 5, n]))), nums(a))

    def solve(d):
        t = ints(d); n, K = t[0], t[1]; a = t[2:2 + n]; c = {0: 1}; s = res = 0
        for x in a:
            s += x & 1; res += c.get(s - K, 0); c[s] = c.get(s, 0) + 1
        return str(res)

    def brute(d):
        t = ints(d); n, K = t[0], t[1]; a = t[2:2 + n]
        return str(sum(1 for i in range(n) for j in range(i, n) if sum(x & 1 for x in a[i:j + 1]) == K))


# 23
@prob('b02_c_one_gap', 'Серия с одним пропуском', 'training', ['Массивы'], 26,
      r"Айгуль отмечает дни: $a_i=1$, если в этот день была ярмарка, и $a_i=0$, если нет. Она вычёркивает из записей ровно один день (любой), после чего смотрит на самую длинную серию подряд идущих единиц. Какой наибольшей длины может получиться серия?",
      r"В первой строке $n$ ($1 \le n \le 2\cdot 10^5$). Во второй — $n$ чисел $a_i \in \{0,1\}$.",
      r"Одно число.", ['7\n1 1 0 1 1 1 0\n'])
class _:
    def gen(r, lv):
        n = N(lv, 2 * 10 ** 5)
        p = r.choice([0.1, 0.5, 0.9, 0.99])
        return '%d\n%s\n' % (n, nums([int(r.random() < p) for _ in range(n)]))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; l = z = best = 0
        for i in range(n):
            z += a[i] == 0
            while z > 1:
                z -= a[l] == 0; l += 1
            best = max(best, i - l)
        return str(best)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; best = 0
        for k in range(n):
            b = a[:k] + a[k + 1:]; cur = 0
            for x in b:
                cur = cur + 1 if x else 0
                best = max(best, cur)
        return str(best)
