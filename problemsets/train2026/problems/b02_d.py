import itertools
from collections import deque
from math import isqrt
from lib import prob, size, nums, ints


def vals(r, n, lo, hi):
    return [r.randint(lo, hi) for _ in range(n)]


def hi_for(lv, small, big):
    return small if lv < 6 else big


def dims(r, lv, cells=200000):
    t = max(2, size(lv, cells))
    n = r.choice([1, 2, isqrt(t), r.randint(1, t)])
    n = max(1, min(n, t))
    return n, max(1, t // n)


def mat_text(g):
    return '\n'.join(nums(row) for row in g) + '\n'


# ---------- next permutation ----------
@prob('b02_d_nextperm', 'Следующий порядок бусин', 'training', ['Массивы'], 28,
      r"Нурлан нанизал бусины с номерами $a_1, \dots, a_n$ (номера могут повторяться). Он хочет переставить бусины так, чтобы получилась ближайшая по порядку расстановка, строго большая текущей, если сравнивать последовательности слева направо. Выведите её или $-1$, если такой нет.",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ целых чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"$n$ чисел через пробел или $-1$.", ['3\n1 3 2\n', '3\n3 2 1\n', '4\n1 5 1 1\n'])
class _:
    def gen(r, lv):
        n = max(2, size(lv, 200000))
        a = vals(r, n, 1, hi_for(lv, 3, 10 ** 9))
        if lv > 2 and lv % 2 == 1:
            a.sort(reverse=True)
            a[-1], a[-2] = a[-2], a[-1]
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        i = n - 2
        while i >= 0 and a[i] >= a[i + 1]: i -= 1
        if i < 0: return '-1'
        j = n - 1
        while a[j] <= a[i]: j -= 1
        a[i], a[j] = a[j], a[i]
        a[i + 1:] = a[i + 1:][::-1]
        return nums(a)

    def brute(d):
        t = ints(d); n = t[0]; a = tuple(t[1:1 + n])
        bigger = [p for p in set(itertools.permutations(a)) if p > a]
        return nums(min(bigger)) if bigger else '-1'


# ---------- merge intervals ----------
def iv_out(res):
    return '\n'.join(['%d' % len(res)] + ['%d %d' % tuple(x) for x in res]) + '\n'


def iv_brute(segs):
    cells = set()
    for l, r_ in segs:
        cells.update(range(2 * l, 2 * r_ + 1))
    res, c = [], sorted(cells)
    s = p = None
    for x in c:
        if s is None: s = p = x
        elif x == p + 1: p = x
        else:
            res.append((s // 2, p // 2)); s = p = x
    res.append((s // 2, p // 2))
    return res


@prob('b02_d_mergeroutes', 'Склейка перегонов', 'training', ['Массивы', 'Сортировка'], 25,
      r"Бакыт отметил на карте $n$ отрезков трассы $[l_i, r_i]$. Отрезки, у которых есть хотя бы одна общая точка (в том числе концевая), он склеивает в один. Выведите итоговые отрезки по возрастанию.",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Далее $n$ строк по два целых числа $l_i$ и $r_i$ ($0 \le l_i \le r_i \le 10^9$).",
      r"В первой строке количество итоговых отрезков $k$, затем $k$ строк с $l$ и $r$.", ['4\n1 3\n8 10\n2 6\n6 7\n', '2\n1 2\n3 4\n'])
class _:
    def gen(r, lv):
        n = max(1, size(lv, 200000))
        C = 25 if lv < 3 else 10 ** 9
        ln = 4 if lv < 3 else max(1, 3 * C // n)
        segs = []
        for _ in range(n):
            l = r.randint(0, C)
            segs.append((l, min(C, l + r.randint(0, ln))))
        return '%d\n%s\n' % (n, '\n'.join('%d %d' % s for s in segs))

    def solve(d):
        t = ints(d); n = t[0]
        s = sorted((t[1 + 2 * i], t[2 + 2 * i]) for i in range(n))
        res = [list(s[0])]
        for l, e in s[1:]:
            if l <= res[-1][1]: res[-1][1] = max(res[-1][1], e)
            else: res.append([l, e])
        return iv_out(res)

    def brute(d):
        t = ints(d); n = t[0]
        return iv_out(iv_brute([(t[1 + 2 * i], t[2 + 2 * i]) for i in range(n)]))


# ---------- insert interval ----------
@prob('b02_d_newstop', 'Новая стоянка', 'training', ['Массивы'], 30,
      r"Вдоль трассы Бишкек — Нарын расположены $k$ занятых участков $[l_i, r_i]$. Они упорядочены и не пересекаются: $r_i < l_{i+1}$. Айгуль занимает ещё один участок $[L, R]$, и все участки с общей точкой сливаются в один. Выведите новый список.",
      r"В первой строке $k$ ($1 \le k \le 10^5$). Далее $k$ строк с $l_i$ и $r_i$ ($0 \le l_i \le r_i \le 10^9$, $r_i < l_{i+1}$), затем строка с $L$ и $R$ ($0 \le L \le R \le 10^9$).",
      r"Число участков $m$ и $m$ строк с границами.", ['3\n1 2\n4 5\n8 9\n3 6\n', '1\n5 6\n1 2\n'])
class _:
    def gen(r, lv):
        k = max(1, size(lv, 100000))
        C = 70 if lv < 3 else 10 ** 9
        p = sorted(r.sample(range(0, C + 1), 2 * k))
        segs = [(p[2 * i], p[2 * i + 1]) for i in range(k)]
        L, R = sorted([r.randint(0, C), r.randint(0, C)])
        if lv > 2 and lv % 2: R = min(C, L + C // k * 3)
        return '%d\n%s\n%d %d\n' % (k, '\n'.join('%d %d' % s for s in segs), L, R)

    def solve(d):
        t = ints(d); k = t[0]
        segs = [(t[1 + 2 * i], t[2 + 2 * i]) for i in range(k)]
        L, R = t[-2], t[-1]; res = []; i = 0
        while i < k and segs[i][1] < L:
            res.append(list(segs[i])); i += 1
        while i < k and segs[i][0] <= R:
            L = min(L, segs[i][0]); R = max(R, segs[i][1]); i += 1
        res.append([L, R])
        res.extend(list(s) for s in segs[i:])
        return iv_out(res)

    def brute(d):
        t = ints(d); k = t[0]
        segs = [(t[1 + 2 * i], t[2 + 2 * i]) for i in range(k)] + [(t[-2], t[-1])]
        return iv_out(iv_brute(segs))


# ---------- rotate matrix ----------
@prob('b02_d_turnmap', 'Повёрнутая карта', 'training', ['Массивы', 'Математика'], 22,
      r"Квадратная карта пастбищ — таблица $n \times n$. Её поворачивают на $90^\circ$ по часовой стрелке $k$ раз. Выведите таблицу после всех поворотов.",
      r"В первой строке $n$ и $k$ ($1 \le n \le 400$, $0 \le k \le 10^9$). Далее $n$ строк по $n$ целых чисел ($|a_{ij}| \le 10^9$).",
      r"$n$ строк по $n$ чисел.", ['2 1\n1 2\n3 4\n'])
class _:
    def gen(r, lv):
        n = max(1, min(400, isqrt(size(lv, 160000))))
        k = r.randint(0, 6) if lv < 3 else r.randint(0, 10 ** 9)
        g = [vals(r, n, -9 if lv < 5 else -10 ** 9, 9 if lv < 5 else 10 ** 9) for _ in range(n)]
        return '%d %d\n%s' % (n, k, mat_text(g))

    def solve(d):
        t = ints(d); n, k = t[0], t[1] % 4
        g = [t[2 + i * n:2 + (i + 1) * n] for i in range(n)]
        for _ in range(k):
            g = [list(x) for x in zip(*g[::-1])]
        return mat_text(g).strip()

    def brute(d):
        t = ints(d); n, k = t[0], t[1]
        g = [t[2 + i * n:2 + (i + 1) * n] for i in range(n)]
        for _ in range(k):
            h = [[0] * n for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    h[j][n - 1 - i] = g[i][j]
            g = h
        return mat_text(g).strip()


# ---------- spiral ----------
@prob('b02_d_spiralfield', 'Спираль на поле', 'training', ['Массивы'], 20,
      r"Поле разбито на таблицу $n \times m$. Нурлан обходит клетки по спирали: начинает в левом верхнем углу, идёт вправо до края, затем вниз, влево, вверх и так далее, не заходя в уже пройденные клетки, пока не обойдёт все. Выведите числа в клетках в порядке обхода.",
      r"В первой строке $n$ и $m$ ($1 \le n, m$, $n \cdot m \le 2 \cdot 10^5$). Далее $n$ строк по $m$ целых чисел ($|a_{ij}| \le 10^9$).",
      r"$n \cdot m$ чисел через пробел.", ['3 3\n1 2 3\n4 5 6\n7 8 9\n'])
class _:
    def gen(r, lv):
        n, m = dims(r, lv)
        g = [vals(r, m, -99, 999) for _ in range(n)]
        return '%d %d\n%s' % (n, m, mat_text(g))

    def solve(d):
        t = ints(d); n, m = t[0], t[1]
        g = [t[2 + i * m:2 + (i + 1) * m] for i in range(n)]
        top, bot, lef, rig = 0, n - 1, 0, m - 1; res = []
        while top <= bot and lef <= rig:
            res.extend(g[top][lef:rig + 1])
            res.extend(g[i][rig] for i in range(top + 1, bot + 1))
            if top < bot:
                res.extend(g[bot][j] for j in range(rig - 1, lef - 1, -1))
            if lef < rig:
                res.extend(g[i][lef] for i in range(bot - 1, top, -1))
            top += 1; bot -= 1; lef += 1; rig -= 1
        return nums(res)

    def brute(d):
        t = ints(d); n, m = t[0], t[1]
        g = [t[2 + i * m:2 + (i + 1) * m] for i in range(n)]
        seen = [[False] * m for _ in range(n)]
        i = j = 0; di, dj = 0, 1; res = []
        for _ in range(n * m):
            res.append(g[i][j]); seen[i][j] = True
            ni, nj = i + di, j + dj
            if not (0 <= ni < n and 0 <= nj < m and not seen[ni][nj]):
                di, dj = dj, -di
                ni, nj = i + di, j + dj
            i, j = ni, nj
        return nums(res)


# ---------- elements more than n/3 ----------
@prob('b02_d_thirdvotes', 'Любимцы жюри', 'training', ['Массивы', 'Структуры данных'], 38,
      r"На конкурсе акынов $n$ зрителей отдали голоса за участников с номерами $a_i$. Участник считается любимцем, если за него проголосовало строго больше трети зрителей. Выведите номера всех любимцев по возрастанию или $-1$, если их нет.",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ целых чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"Номера любимцев через пробел или $-1$.", ['6\n3 1 3 2 3 1\n', '5\n1 2 3 4 5\n'])
class _:
    def gen(r, lv):
        n = max(1, size(lv, 200000))
        C = 4 if lv < 3 else 10 ** 9
        fav = [r.randint(1, C) for _ in range(r.randint(1, 3))]
        w = r.uniform(0.2, 0.9)
        a = [r.choice(fav) if r.random() < w else r.randint(1, C) for _ in range(n)]
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        c1 = c2 = None; k1 = k2 = 0
        for x in a:
            if x == c1: k1 += 1
            elif x == c2: k2 += 1
            elif k1 == 0: c1, k1 = x, 1
            elif k2 == 0: c2, k2 = x, 1
            else: k1 -= 1; k2 -= 1
        cnt = {}
        for c in (c1, c2):
            if c is not None: cnt[c] = 0
        for x in a:
            if x in cnt: cnt[x] += 1
        res = sorted(c for c, v in cnt.items() if 3 * v > n)
        return nums(res) if res else '-1'

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        res = sorted(x for x in set(a) if 3 * a.count(x) > n)
        return nums(res) if res else '-1'


# ---------- stock with gap ----------
@prob('b02_d_wooldelay', 'Выдержанная шерсть', 'training', ['Массивы', 'Жадные'], 27,
      r"Цена шерсти на базаре в $i$-й день равна $p_i$. Айгуль покупает шерсть в один день и продаёт в другой не раньше чем через $d$ дней после покупки. Какую наибольшую прибыль она получит? Если выгодной сделки нет, она ничего не делает и прибыль равна $0$.",
      r"В первой строке $n$ и $d$ ($1 \le d \le n \le 2 \cdot 10^5$). Во второй — $n$ чисел $p_i$ ($1 \le p_i \le 10^9$).",
      r"Наибольшая прибыль.", ['6 2\n7 1 5 3 6 4\n', '3 1\n9 5 2\n'])
class _:
    def gen(r, lv):
        n = max(2, size(lv, 200000))
        d = r.randint(1, max(1, n // 3)) if r.random() < 0.7 else r.randint(1, n)
        a = vals(r, n, 1, hi_for(lv, 20, 10 ** 9))
        return '%d %d\n%s\n' % (n, d, nums(a))

    def solve(d):
        t = ints(d); n, g = t[0], t[1]; p = t[2:2 + n]
        best = 0; mn = 10 ** 18
        for j in range(g, n):
            mn = min(mn, p[j - g]); best = max(best, p[j] - mn)
        return str(best)

    def brute(d):
        t = ints(d); n, g = t[0], t[1]; p = t[2:2 + n]
        return str(max([0] + [p[j] - p[i] for i in range(n) for j in range(i + g, n)]))


# ---------- jump game II ----------
@prob('b02_d_passjumps', 'Перевалы Нарына', 'training', ['Массивы', 'Жадные'], 35,
      r"Нурлан стоит на первом из $n$ перевалов. С перевала $i$ он может спуститься на любой из следующих $a_i$ перевалов (на $1, 2, \dots, a_i$ вперёд). Какое наименьшее число переходов нужно, чтобы добраться до $n$-го перевала? Если это невозможно, выведите $-1$.",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^9$).",
      r"Минимальное число переходов или $-1$.", ['5\n2 3 1 1 4\n', '4\n1 0 3 1\n'])
class _:
    def gen(r, lv):
        n = max(1, size(lv, 200000))
        k = r.choice([2, 3, 5, 20]) if lv > 2 else 3
        a = [r.randint(0, k) if r.random() < 0.9 else r.randint(0, 10 ** 9 if lv > 6 else k) for _ in range(n)]
        if lv > 2 and lv % 3 != 0:
            a = [max(1, x) for x in a]
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        cur = far = steps = 0
        for i in range(n - 1):
            far = max(far, i + a[i])
            if i == cur:
                if far <= i: return '-1'
                steps += 1; cur = far
                if cur >= n - 1: break
        return str(steps) if cur >= n - 1 else '-1'

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        INF = 10 ** 9; dist = [INF] * n; dist[0] = 0
        for i in range(n):
            if dist[i] < INF:
                for j in range(i + 1, min(n, i + a[i] + 1)):
                    dist[j] = min(dist[j], dist[i] + 1)
        return str(dist[-1] if dist[-1] < INF else -1)


# ---------- min swaps to sort permutation ----------
@prob('b02_d_buckets', 'Раскладка вёдер', 'training', ['Массивы', 'Математика'], 24,
      r"В ряд стоят $n$ вёдер с номерами $1 \dots n$, каждый номер встречается ровно один раз. За ход можно поменять местами любые два ведра. Какое наименьшее число ходов нужно, чтобы расставить вёдра по порядку номеров?",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — перестановка чисел от $1$ до $n$.",
      r"Наименьшее число ходов.", ['4\n2 1 4 3\n', '3\n3 1 2\n'])
class _:
    def gen(r, lv):
        n = max(1, size(lv, 200000))
        a = list(range(1, n + 1))
        r.shuffle(a)
        if lv > 2 and lv % 3 == 0:
            a = list(range(1, n + 1))
            for _ in range(n // 10 + 1):
                i, j = r.randrange(n), r.randrange(n); a[i], a[j] = a[j], a[i]
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; seen = [False] * n; cyc = 0
        for i in range(n):
            if not seen[i]:
                cyc += 1; j = i
                while not seen[j]:
                    seen[j] = True; j = a[j] - 1
        return str(n - cyc)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; cnt = 0
        for i in range(n):
            while a[i] != i + 1:
                j = a[i] - 1; a[i], a[j] = a[j], a[i]; cnt += 1
        return str(cnt)


# ---------- inversions ----------
@prob('b02_d_queuebazaar', 'Очередь за лепёшками', 'training', ['Массивы', 'Структуры данных'], 42,
      r"В очереди за лепёшками стоят $n$ человек, у $i$-го возраст $a_i$. Пара людей «обижена», если старший стоит раньше младшего (то есть $i < j$ и $a_i > a_j$). Сколько обиженных пар?",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"Количество пар.", ['5\n3 1 2 5 4\n', '3\n5 5 5\n'])
class _:
    def gen(r, lv):
        n = max(1, size(lv, 200000))
        a = vals(r, n, 1, hi_for(lv, 6, 10 ** 9))
        if lv > 4 and lv % 2: a.sort(reverse=True)
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        rk = {v: i + 1 for i, v in enumerate(sorted(set(a)))}; m = len(rk)
        tree = [0] * (m + 1); res = 0
        for i, v in enumerate(a):
            x = rk[v]; s = 0; k = x
            while k > 0: s += tree[k]; k -= k & -k
            res += i - s
            while x <= m: tree[x] += 1; x += x & -x
        return str(res)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        return str(sum(1 for i in range(n) for j in range(i + 1, n) if a[i] > a[j]))


# ---------- largest rectangle in histogram ----------
@prob('b02_d_signboard', 'Вывеска на заборе', 'training', ['Массивы', 'Структуры данных'], 48,
      r"Забор состоит из $n$ досок шириной 1 и высотой $h_i$. Чолпон хочет повесить прямоугольную вывеску так, чтобы она целиком лежала на заборе и закрывала подряд идущие доски. Какова наибольшая площадь вывески?",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ чисел $h_i$ ($0 \le h_i \le 10^9$).",
      r"Наибольшая площадь.", ['6\n2 1 5 6 2 3\n', '2\n0 0\n'])
class _:
    def gen(r, lv):
        n = max(1, size(lv, 200000))
        hi = hi_for(lv, 6, 10 ** 9)
        a = vals(r, n, 0, hi)
        if lv > 3 and lv % 3 == 0:
            a = [r.randint(hi * 9 // 10, hi) for _ in range(n)]
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n] + [0]
        st = []; best = 0
        for i, h in enumerate(a):
            s = i
            while st and st[-1][1] >= h:
                s, hh = st.pop(); best = max(best, hh * (i - s))
            st.append((s, h))
        return str(best)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; best = 0
        for i in range(n):
            m = a[i]
            for j in range(i, n):
                m = min(m, a[j]); best = max(best, m * (j - i + 1))
        return str(best)


# ---------- first missing positive ----------
@prob('b02_d_freeticket', 'Свободный талон', 'training', ['Массивы', 'Математика'], 18,
      r"В поликлинике Оша выданы талоны с номерами $a_i$ (в списке есть и ошибочные числа, нули и отрицательные). Какой наименьший положительный номер ещё не выдан?",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ целых чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Наименьший положительный номер, которого нет среди $a_i$.", ['4\n3 4 -1 1\n', '3\n7 8 9\n'])
class _:
    def gen(r, lv):
        n = max(1, size(lv, 200000))
        m = r.randint(0, n)
        a = list(range(1, m + 1))
        if m and lv > 1 and r.random() < 0.7: a.pop(r.randrange(m))
        a += [r.choice([r.randint(-10 ** 9, 0), r.randint(1, 10 ** 9), r.randint(1, n + 3)]) for _ in range(n - len(a))]
        if lv < 3: a = [x if abs(x) < 12 else r.randint(-5, 9) for x in a]
        r.shuffle(a)
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; s = set(t[1:1 + n]); k = 1
        while k in s: k += 1
        return str(k)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        for k in range(1, n + 3):
            if k not in a: return str(k)


# ---------- next taller ----------
@prob('b02_d_taller', 'Ближайшая вершина выше', 'training', ['Массивы', 'Структуры данных'], 36,
      r"Вдоль хребта идут $n$ вершин, высота $i$-й равна $h_i$. Для каждой вершины найдите, через сколько вершин справа встречается первая строго более высокая. Если справа выше нет, выведите $0$.",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ чисел $h_i$ ($1 \le h_i \le 10^9$).",
      r"$n$ чисел через пробел: расстояния до ближайшей более высокой вершины справа или $0$.", ['6\n73 74 75 71 69 76\n'])
class _:
    def gen(r, lv):
        n = max(1, size(lv, 200000))
        a = vals(r, n, 1, hi_for(lv, 8, 10 ** 9))
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; res = [0] * n; st = []
        for i in range(n):
            while st and a[st[-1]] < a[i]:
                j = st.pop(); res[j] = i - j
            st.append(i)
        return nums(res)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; res = []
        for i in range(n):
            res.append(next((j - i for j in range(i + 1, n) if a[j] > a[i]), 0))
        return nums(res)


# ---------- container with most water ----------
@prob('b02_d_twoposts', 'Водоём между столбами', 'training', ['Массивы', 'Жадные'], 33,
      r"Вдоль арыка стоят $n$ столбов высотой $h_i$, расстояние между соседними равно 1. Между двумя столбами $i < j$ можно устроить водоём: его ширина $j - i$, а высота равна меньшей из двух высот. Найдите наибольшую площадь $(j-i)\cdot\min(h_i, h_j)$.",
      r"В первой строке $n$ ($2 \le n \le 2 \cdot 10^5$). Во второй — $n$ чисел $h_i$ ($0 \le h_i \le 10^9$).",
      r"Наибольшая площадь.", ['9\n1 8 6 2 5 4 8 3 7\n', '2\n3 4\n'])
class _:
    def gen(r, lv):
        n = max(2, size(lv, 200000))
        a = vals(r, n, 0, hi_for(lv, 9, 10 ** 9))
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; i, j = 0, n - 1; best = 0
        while i < j:
            best = max(best, (j - i) * min(a[i], a[j]))
            if a[i] < a[j]: i += 1
            else: j -= 1
        return str(best)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        return str(max((j - i) * min(a[i], a[j]) for i in range(n) for j in range(i + 1, n)))


# ---------- subarrays with sum divisible by k ----------
@prob('b02_d_multrev', 'Кратные поступления', 'training', ['Массивы', 'Математика'], 40,
      r"Бакыт записал дневные поступления кафе $a_1, \dots, a_n$ (бывают и убытки, то есть отрицательные числа). Сколько существует непустых промежутков подряд идущих дней, сумма поступлений за которые делится на $k$ нацело?",
      r"В первой строке $n$ и $k$ ($1 \le n \le 2 \cdot 10^5$, $1 \le k \le 10^9$). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Количество промежутков.", ['5 5\n4 5 0 -2 -3\n', '3 7\n1 2 3\n'])
class _:
    def gen(r, lv):
        n = max(1, size(lv, 200000))
        k = r.randint(1, 4) if lv < 3 else r.choice([1, 2, 7, 10, 1000, 10 ** 9, r.randint(1, n)])
        a = vals(r, n, -hi_for(lv, 9, 10 ** 9), hi_for(lv, 9, 10 ** 9))
        return '%d %d\n%s\n' % (n, k, nums(a))

    def solve(d):
        t = ints(d); n, k = t[0], t[1]; a = t[2:2 + n]
        cnt = {0: 1}; s = res = 0
        for x in a:
            s = (s + x) % k
            c = cnt.get(s, 0); res += c; cnt[s] = c + 1
        return str(res)

    def brute(d):
        t = ints(d); n, k = t[0], t[1]; a = t[2:2 + n]
        return str(sum(1 for i in range(n) for j in range(i, n) if sum(a[i:j + 1]) % k == 0))


# ---------- longest consecutive values ----------
@prob('b02_d_ticketrun', 'Цепочка номеров', 'training', ['Массивы', 'Математика'], 26,
      r"У Айгуль есть $n$ карточек с номерами $a_i$ (номера могут повторяться). Она хочет выложить из них самую длинную цепочку, в которой номера идут подряд: $x, x+1, x+2, \dots$ Одинаковые номера в цепочку дважды не входят. Найдите наибольшую длину цепочки.",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Длина цепочки.", ['6\n100 4 200 1 3 2\n', '4\n5 5 5 5\n'])
class _:
    def gen(r, lv):
        n = max(1, size(lv, 200000))
        R = 6 if lv < 3 else r.choice([n, 2 * n, 10 ** 9])
        a = vals(r, n, -R, R)
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; s = set(t[1:1 + n]); best = 0
        for x in s:
            if x - 1 not in s:
                y = x
                while y + 1 in s: y += 1
                best = max(best, y - x + 1)
        return str(best)

    def brute(d):
        t = ints(d); n = t[0]; s = sorted(set(t[1:1 + n])); best = cur = 1
        for i in range(1, len(s)):
            cur = cur + 1 if s[i] == s[i - 1] + 1 else 1
            best = max(best, cur)
        return str(best)


# ---------- sliding window max ----------
@prob('b02_d_windowpeak', 'Рекорды в окне ярмарки', 'training', ['Массивы', 'Структуры данных'], 44,
      r"Продажи на ярмарке по дням: $a_1, \dots, a_n$. Для каждого окна из $k$ подряд идущих дней найдите наибольшие продажи в нём.",
      r"В первой строке $n$ и $k$ ($1 \le k \le n \le 2 \cdot 10^5$). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"$n - k + 1$ чисел через пробел: максимумы окон слева направо.", ['8 3\n1 3 -1 -3 5 3 6 7\n'])
class _:
    def gen(r, lv):
        n = max(2, size(lv, 200000))
        k = r.randint(1, n) if r.random() < 0.4 else r.randint(1, max(1, min(n, 1 + n // 4)))
        a = vals(r, n, -hi_for(lv, 9, 10 ** 9), hi_for(lv, 9, 10 ** 9))
        return '%d %d\n%s\n' % (n, k, nums(a))

    def solve(d):
        t = ints(d); n, k = t[0], t[1]; a = t[2:2 + n]; q = deque(); res = []
        for i in range(n):
            while q and a[q[-1]] <= a[i]: q.pop()
            q.append(i)
            if q[0] <= i - k: q.popleft()
            if i >= k - 1: res.append(a[q[0]])
        return nums(res)

    def brute(d):
        t = ints(d); n, k = t[0], t[1]; a = t[2:2 + n]
        return nums([max(a[i:i + k]) for i in range(n - k + 1)])


# ---------- set matrix zeroes ----------
@prob('b02_d_lampsout', 'Погасшие лампы', 'training', ['Массивы'], 15,
      r"На стене чайханы в таблице $n \times m$ висят гирлянды: в клетке записана яркость лампы. Если лампа перегорела (яркость $0$), то гаснут все лампы в её строке и в её столбце. Выведите таблицу после того, как все такие лампы погасли.",
      r"В первой строке $n$ и $m$ ($1 \le n, m$, $n \cdot m \le 2 \cdot 10^5$). Далее $n$ строк по $m$ чисел ($0 \le a_{ij} \le 10^9$).",
      r"$n$ строк по $m$ чисел.", ['3 3\n1 1 1\n1 0 1\n1 1 1\n'])
class _:
    def gen(r, lv):
        n, m = dims(r, lv)
        g = [vals(r, m, 1, 9 if lv < 6 else 10 ** 9) for _ in range(n)]
        for _ in range(r.randint(0, 3 if lv > 2 else 2)):
            g[r.randrange(n)][r.randrange(m)] = 0
        return '%d %d\n%s' % (n, m, mat_text(g))

    def solve(d):
        t = ints(d); n, m = t[0], t[1]
        g = [t[2 + i * m:2 + (i + 1) * m] for i in range(n)]
        rows = {i for i in range(n) if 0 in g[i]}
        cols = {j for i in range(n) for j in range(m) if g[i][j] == 0}
        return mat_text([[0 if i in rows or j in cols else g[i][j] for j in range(m)] for i in range(n)]).strip()

    def brute(d):
        t = ints(d); n, m = t[0], t[1]
        g = [t[2 + i * m:2 + (i + 1) * m] for i in range(n)]
        res = []
        for i in range(n):
            res.append([0 if any(g[i][x] == 0 for x in range(m)) or any(g[y][j] == 0 for y in range(n)) else g[i][j] for j in range(m)])
        return mat_text(res).strip()


# ---------- candy ----------
@prob('b02_d_prizes', 'Награды олимпиадникам', 'training', ['Массивы', 'Жадные'], 45,
      r"В ряд стоят $n$ школьников с рейтингами $r_i$. Каждому надо выдать хотя бы одну медаль. Если у ученика рейтинг строго выше, чем у соседа (слева или справа), то медалей у него должно быть строго больше, чем у этого соседа. Какое наименьшее число медалей нужно?",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ чисел $r_i$ ($1 \le r_i \le 10^9$).",
      r"Наименьшее общее число медалей.", ['3\n1 0 2\n', '3\n1 2 2\n'])
class _:
    def gen(r, lv):
        n = max(1, size(lv, 200000))
        a = vals(r, n, 1, hi_for(lv, 5, 10 ** 9))
        if lv > 3 and lv % 3 == 0: a.sort()
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; c = [1] * n
        for i in range(1, n):
            if a[i] > a[i - 1]: c[i] = c[i - 1] + 1
        for i in range(n - 2, -1, -1):
            if a[i] > a[i + 1]: c[i] = max(c[i], c[i + 1] + 1)
        return str(sum(c))

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; c = [1] * n; ch = True
        while ch:
            ch = False
            for i in range(n):
                for j in (i - 1, i + 1):
                    if 0 <= j < n and a[i] > a[j] and c[i] <= c[j]:
                        c[i] = c[j] + 1; ch = True
        return str(sum(c))


# ---------- longest positive product ----------
@prob('b02_d_goodstreak', 'Прибыльная серия', 'training', ['Массивы', 'Математика'], 32,
      r"За $i$-й день дела Нурлана изменились в $a_i$ раз (отрицательное число — убыток со сменой знака, ноль — остановка дел). Серия — это подряд идущие дни, её итог — произведение чисел $a_i$ в ней. Какова наибольшая длина серии с положительным итогом?",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ целых чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Наибольшая длина серии или $0$.", ['6\n1 -2 -3 4 0 5\n', '3\n-1 0 -2\n'])
class _:
    def gen(r, lv):
        n = max(1, size(lv, 200000))
        z = r.choice([0.0, 0.01, 0.2]) if lv > 2 else 0.2
        a = [0 if r.random() < z else r.choice([-1, 1]) * r.randint(1, hi_for(lv, 5, 10 ** 9)) for _ in range(n)]
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; best = 0
        pos = neg = 0
        for x in a:
            if x == 0: pos = neg = 0
            elif x > 0: pos, neg = pos + 1, (neg + 1 if neg else 0)
            else: pos, neg = (neg + 1 if neg else 0), pos + 1
            best = max(best, pos)
        return str(best)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; best = 0
        for i in range(n):
            p = 1
            for j in range(i, n):
                p *= (a[j] > 0) - (a[j] < 0)
                if p > 0: best = max(best, j - i + 1)
        return str(best)


# ---------- pivot ----------
@prob('b02_d_scalepoint', 'Точка опоры весов', 'training', ['Массивы'], 10,
      r"Доска с грузами лежит на опоре. Вес груза на $i$-м месте равен $a_i$ (бывают и подвесные, то есть отрицательные грузы). Нужно найти место, где сумма грузов слева равна сумме грузов справа; сам груз на этом месте не считается. Выведите наименьший номер такого места или $-1$.",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Номер места (с единицы) или $-1$.", ['6\n1 7 3 6 5 6\n', '3\n1 2 3\n'])
class _:
    def gen(r, lv):
        n = max(1, size(lv, 200000))
        h = hi_for(lv, 3, 1000)
        a = vals(r, n, -h, h)
        if lv > 0 and n > 1 and r.random() < 0.7:
            p = r.randrange(n - 1)
            a[n - 1] += sum(a[:p]) - sum(a[p + 1:])
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; tot = sum(a); left = 0
        for i in range(n):
            if left == tot - left - a[i]: return str(i + 1)
            left += a[i]
        return '-1'

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        for i in range(n):
            if sum(a[:i]) == sum(a[i + 1:]): return str(i + 1)
        return '-1'


# ---------- anti-diagonals ----------
@prob('b02_d_diagwalk', 'Обход караван-сарая по диагоналям', 'training', ['Массивы'], 17,
      r"Двор караван-сарая разбит на клетки $n \times m$. Сторож обходит их по диагоналям: сначала клетку $(1,1)$, затем клетки с $i+j=3$, потом с $i+j=4$ и так далее. Внутри диагонали он идёт сверху вниз (от меньшего $i$ к большему). Выведите числа в клетках в порядке обхода.",
      r"В первой строке $n$ и $m$ ($1 \le n, m$, $n \cdot m \le 2 \cdot 10^5$). Далее $n$ строк по $m$ целых чисел ($|a_{ij}| \le 10^9$).",
      r"$n \cdot m$ чисел через пробел.", ['2 3\n1 2 3\n4 5 6\n'])
class _:
    def gen(r, lv):
        n, m = dims(r, lv)
        g = [vals(r, m, -99, 999) for _ in range(n)]
        return '%d %d\n%s' % (n, m, mat_text(g))

    def solve(d):
        t = ints(d); n, m = t[0], t[1]; g = t[2:2 + n * m]; res = []
        for s in range(n + m - 1):
            for i in range(max(0, s - m + 1), min(n - 1, s) + 1):
                res.append(g[i * m + s - i])
        return nums(res)

    def brute(d):
        t = ints(d); n, m = t[0], t[1]; g = t[2:2 + n * m]
        cells = sorted((i + j, i, g[i * m + j]) for i in range(n) for j in range(m))
        return nums([c[2] for c in cells])


# ---------- circular max subarray ----------
@prob('b02_d_ringprofit', 'Прибыль на кольцевой трассе', 'training', ['Массивы', 'DP'], 46,
      r"Кольцевая трасса вокруг Иссык-Куля состоит из $n$ перегонов по кругу; на $i$-м перегоне прибыль равна $a_i$ (возможен убыток). Маршрут — это подряд идущие перегоны, в том числе проходящие через стык последнего и первого; один перегон нельзя проехать дважды. Найдите наибольшую суммарную прибыль маршрута хотя бы из одного перегона.",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Наибольшая суммарная прибыль.", ['5\n5 -3 5 -4 2\n', '3\n-3 -2 -3\n'])
class _:
    def gen(r, lv):
        n = max(1, size(lv, 200000))
        h = hi_for(lv, 6, 10 ** 9)
        a = vals(r, n, -h, h)
        if lv > 3 and lv % 3 == 0:
            a = vals(r, n, -h, 0)
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        mx = cmx = mn = cmn = a[0]
        for x in a[1:]:
            cmx = max(x, cmx + x); mx = max(mx, cmx)
            cmn = min(x, cmn + x); mn = min(mn, cmn)
        tot = sum(a)
        return str(mx if mx < 0 or mn == tot else max(mx, tot - mn))

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; best = -10 ** 18
        for i in range(n):
            s = 0
            for k in range(n):
                s += a[(i + k) % n]; best = max(best, s)
        return str(best)


# ---------- group ones ----------
@prob('b02_d_flockgather', 'Собрать отару', 'training', ['Массивы', 'Жадные'], 34,
      r"На лугу в ряд расположены $n$ мест; на каждом либо стоит овца ($1$), либо пусто ($0$). За ход можно поменять местами содержимое любых двух мест. Какое наименьшее число ходов нужно, чтобы все овцы стояли подряд, без пустых мест между ними?",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ чисел $0$ или $1$.",
      r"Наименьшее число ходов.", ['6\n1 0 1 0 0 1\n', '3\n0 0 0\n'])
class _:
    def gen(r, lv):
        n = max(1, size(lv, 200000))
        p = r.choice([0.1, 0.3, 0.5, 0.8])
        a = [1 if r.random() < p else 0 for _ in range(n)]
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; k = sum(a)
        if k == 0: return '0'
        w = sum(a[:k]); best = w
        for i in range(k, n):
            w += a[i] - a[i - k]; best = max(best, w)
        return str(k - best)

    def brute(d):
        t = ints(d); n = t[0]; a = tuple(t[1:1 + n]); k = sum(a)
        goal = {tuple([0] * i + [1] * k + [0] * (n - i - k)) for i in range(n - k + 1)}
        dist = {a: 0}; q = deque([a])
        while q:
            s = q.popleft()
            if s in goal: return str(dist[s])
            for i in range(n):
                for j in range(i + 1, n):
                    if s[i] != s[j]:
                        u = list(s); u[i], u[j] = u[j], u[i]; u = tuple(u)
                        if u not in dist:
                            dist[u] = dist[s] + 1; q.append(u)


# ---------- min cost climb ----------
@prob('b02_d_alakul', 'Подъём к Ала-Кулю', 'training', ['Массивы', 'DP'], 14,
      r"К озеру Ала-Куль ведёт тропа с $n$ лагерями, остановка в $i$-м стоит $c_i$ сомов. Группа Айгуль начинает путь с первого или второго лагеря (платя за него) и за переход может подняться на 1 или 2 лагеря вперёд. Озеро лежит сразу за $n$-м лагерем, и дойти до него можно из лагеря $n$ или $n-1$. Какова наименьшая суммарная плата за остановки?",
      r"В первой строке $n$ ($2 \le n \le 2 \cdot 10^5$). Во второй — $n$ чисел $c_i$ ($0 \le c_i \le 10^9$).",
      r"Наименьшая плата.", ['3\n10 15 20\n', '6\n1 100 1 1 1 100\n'])
class _:
    def gen(r, lv):
        n = max(2, size(lv, 200000))
        a = vals(r, n, 0, hi_for(lv, 9, 10 ** 9))
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; c = t[1:1 + n]
        p2, p1 = c[0], c[1]
        for i in range(2, n):
            p2, p1 = p1, min(p1, p2) + c[i]
        return str(min(p1, p2))

    def brute(d):
        t = ints(d); n = t[0]; c = t[1:1 + n]

        def go(i):
            if i >= n: return 0
            return c[i] + min(go(i + 1), go(i + 2))
        return str(min(go(0), go(1)))
