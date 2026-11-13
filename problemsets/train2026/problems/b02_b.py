import bisect
from lib import prob, size, nums, ints

BIG = 10 ** 5


def H(lv, big):
    return 3 if lv < 3 else big


def segs(r, n, q, short=False):
    out = []
    for _ in range(q):
        l = r.randint(1, n)
        rr = min(n, l + r.randint(0, 6)) if short and r.random() < 0.5 else r.randint(l, n)
        out.append((l, rr))
    return out


@prob('b02_b_milk_days', 'Удои по дням', 'training', ['Массивы'], 10,
      r"Бакыт записывает, сколько литров молока дала корова в каждый из $n$ дней. Ответьте на $q$ вопросов: сколько литров получено с дня $l$ по день $r$ включительно.",
      r"В первой строке $n$ и $q$ ($1 \le n, q \le 2 \cdot 10^5$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^9$). Далее $q$ строк с $l$ и $r$ ($1 \le l \le r \le n$).",
      r"Для каждого вопроса — сумму на отдельной строке.", ['5 2\n3 1 4 1 5\n1 3\n2 5\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); q = size(lv, BIG); hi = H(lv, 10 ** 9)
        a = [r.randint(0, hi) for _ in range(n)]
        return '%d %d\n%s\n%s\n' % (n, q, nums(a), '\n'.join('%d %d' % s for s in segs(r, n, q)))

    def solve(d):
        t = ints(d); n, q = t[0], t[1]; p = [0]
        for x in t[2:2 + n]: p.append(p[-1] + x)
        o = t[2 + n:]
        return '\n'.join(str(p[o[2 * i + 1]] - p[o[2 * i] - 1]) for i in range(q))

    def brute(d):
        t = ints(d); n, q = t[0], t[1]; a = t[2:2 + n]; o = t[2 + n:]
        return '\n'.join(str(sum(a[o[2 * i] - 1:o[2 * i + 1]])) for i in range(q))


@prob('b02_b_snow_road', 'Снегопад вдоль дороги', 'training', ['Массивы'], 22,
      r"Вдоль дороги Бишкек — Нарын $n$ постов, на $i$-м сейчас лежит $a_i$ см снега. Прошло $q$ снегопадов: $j$-й добавил $x_j$ см на всех постах с $l_j$ по $r_j$ (если $x_j<0$, снег растаял). Сколько снега на каждом посту?",
      r"В первой строке $n$ и $q$ ($1 \le n, q \le 2 \cdot 10^5$). Во второй — $n$ чисел $a_i$. Далее $q$ строк: $l_j$, $r_j$, $x_j$ ($1 \le l_j \le r_j \le n$, $|x_j| \le 10^4$, $|a_i| \le 10^9$).",
      r"$n$ чисел через пробел.", ['5 2\n0 0 0 0 0\n1 3 2\n2 5 -1\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); q = size(lv, BIG); hi = H(lv, 10 ** 4)
        a = [r.randint(-hi, hi) for _ in range(n)]
        u = ['%d %d %d' % (l, rr, r.randint(-hi, hi)) for l, rr in segs(r, n, q)]
        return '%d %d\n%s\n%s\n' % (n, q, nums(a), '\n'.join(u))

    def solve(d):
        t = ints(d); n, q = t[0], t[1]; a = t[2:2 + n]; o = t[2 + n:]; df = [0] * (n + 2)
        for i in range(q):
            l, rr, x = o[3 * i:3 * i + 3]; df[l] += x; df[rr + 1] -= x
        s = 0; res = []
        for i in range(n):
            s += df[i + 1]; res.append(a[i] + s)
        return nums(res)

    def brute(d):
        t = ints(d); n, q = t[0], t[1]; a = t[2:2 + n]; o = t[2 + n:]
        for i in range(q):
            l, rr, x = o[3 * i:3 * i + 3]
            for j in range(l - 1, rr): a[j] += x
        return nums(a)


@prob('b02_b_long_route', 'Длинный маршрут по Нарыну', 'training', ['Массивы', 'Структуры данных'], 35,
      r"Айгуль планирует маршрут по $n$ селам Нарынской области. Заезд в $i$-е село приносит $a_i$ сомов (может быть отрицательным). Нужно проехать подряд не менее $L$ сёл. Какую наибольшую сумму можно получить?",
      r"В первой строке $n$ и $L$ ($1 \le L \le n \le 2 \cdot 10^5$). Во второй — $n$ целых чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Максимальная сумма.", ['5 2\n-3 4 -1 -2 5\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); hi = H(lv, 10 ** 9)
        l = r.randint(1, n) if r.random() < 0.5 else r.randint(1, min(n, 5))
        return '%d %d\n%s\n' % (n, l, nums([r.randint(-hi, hi) for _ in range(n)]))

    def solve(d):
        t = ints(d); n, l = t[0], t[1]; p = [0]
        for x in t[2:2 + n]: p.append(p[-1] + x)
        best = None; mn = 10 ** 30
        for j in range(l, n + 1):
            mn = min(mn, p[j - l]); v = p[j] - mn
            if best is None or v > best: best = v
        return str(best)

    def brute(d):
        t = ints(d); n, l = t[0], t[1]; a = t[2:2 + n]
        return str(max(sum(a[i:j]) for i in range(n) for j in range(i + l, n + 1)))


@prob('b02_b_flour_others', 'Урожай без грядки', 'training', ['Массивы', 'Математика'], 28,
      r"На $n$ грядках выросло по $a_i$ кг урожая. Для каждой грядки $i$ найдите произведение урожаев всех остальных грядок по модулю $m$. Учтите, что $m$ может быть составным, а в массиве бывают нули.",
      r"В первой строке $n$ и $m$ ($2 \le n \le 2 \cdot 10^5$, $2 \le m \le 10^9$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^9$).",
      r"$n$ чисел через пробел.", ['4 10\n1 2 3 4\n'])
class _:
    def gen(r, lv):
        n = max(2, size(lv, BIG)); hi = H(lv, 10 ** 9)
        m = r.randint(2, 12) if lv < 3 else r.choice([6, 100, 1000, 999999937, 10 ** 9, 720720])
        a = [r.randint(0, hi) for _ in range(n)]
        if lv > 3 and r.random() < 0.4: a[r.randrange(n)] = 0
        return '%d %d\n%s\n' % (n, m, nums(a))

    def solve(d):
        t = ints(d); n, m = t[0], t[1]; a = t[2:2 + n]; pre = [1 % m] * (n + 1)
        for i in range(n): pre[i + 1] = pre[i] * a[i] % m
        res = [0] * n; suf = 1 % m
        for i in range(n - 1, -1, -1):
            res[i] = pre[i] * suf % m; suf = suf * a[i] % m
        return nums(res)

    def brute(d):
        t = ints(d); n, m = t[0], t[1]; a = t[2:2 + n]; out = []
        for i in range(n):
            p = 1 % m
            for j in range(n):
                if j != i: p = p * a[j] % m
            out.append(p)
        return nums(out)


@prob('b02_b_apple_grid', 'Яблоневый сад в клетку', 'training', ['Массивы'], 25,
      r"Сад Бакыта — таблица $n \times m$, в клетке $(i,j)$ растёт $a_{ij}$ яблок. Ответьте на $q$ вопросов: сколько яблок в прямоугольнике с углами $(r_1,c_1)$ и $(r_2,c_2)$.",
      r"В первой строке $n$, $m$ и $q$ ($1 \le n \cdot m \le 2 \cdot 10^5$, $1 \le q \le 2 \cdot 10^5$). Далее $n$ строк по $m$ чисел $a_{ij}$ ($|a_{ij}| \le 10^4$). Далее $q$ строк: $r_1, c_1, r_2, c_2$ ($1 \le r_1 \le r_2 \le n$, $1 \le c_1 \le c_2 \le m$).",
      r"Для каждого вопроса — сумму на отдельной строке.", ['2 3 2\n1 2 3\n4 5 6\n1 1 2 2\n2 2 2 3\n'])
class _:
    def gen(r, lv):
        N = size(lv, BIG); q = size(lv, BIG); hi = H(lv, 10 ** 4)
        n = max(1, min(N, int(N ** 0.5 * r.uniform(0.3, 2)))); m = max(1, N // n)
        g = [nums([r.randint(-hi, hi) for _ in range(m)]) for _ in range(n)]
        qs = []
        for _ in range(q):
            r1 = r.randint(1, n); r2 = r.randint(r1, n); c1 = r.randint(1, m); c2 = r.randint(c1, m)
            qs.append('%d %d %d %d' % (r1, c1, r2, c2))
        return '%d %d %d\n%s\n%s\n' % (n, m, q, '\n'.join(g), '\n'.join(qs))

    def solve(d):
        t = ints(d); n, m, q = t[:3]; v = t[3:]; p = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(n):
            row = 0
            for j in range(m):
                row += v[i * m + j]; p[i + 1][j + 1] = p[i][j + 1] + row
        o = v[n * m:]; res = []
        for k in range(q):
            r1, c1, r2, c2 = o[4 * k:4 * k + 4]
            res.append(p[r2][c2] - p[r1 - 1][c2] - p[r2][c1 - 1] + p[r1 - 1][c1 - 1])
        return '\n'.join(map(str, res))

    def brute(d):
        t = ints(d); n, m, q = t[:3]; v = t[3:]; o = v[n * m:]; res = []
        for k in range(q):
            r1, c1, r2, c2 = o[4 * k:4 * k + 4]
            res.append(sum(v[i * m + j] for i in range(r1 - 1, r2) for j in range(c1 - 1, c2)))
        return '\n'.join(map(str, res))


@prob('b02_b_short_shift', 'Короткая смена', 'training', ['Массивы', 'Двоичный поиск'], 28,
      r"Нурлан разгружает машины: на $i$-й машине заработок $a_i$ сомов ($a_i>0$). Смена — несколько машин подряд. Какова наименьшая длина смены, на которой заработок не менее $S$? Если это невозможно, выведите $-1$.",
      r"В первой строке $n$ и $S$ ($1 \le n \le 2 \cdot 10^5$, $1 \le S \le 2 \cdot 10^9$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^4$).",
      r"Длина смены или $-1$.", ['5 7\n2 3 1 2 4\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); hi = 5 if lv < 3 else 10 ** 4
        a = [r.randint(1, hi) for _ in range(n)]; tot = sum(a)
        s = r.randint(1, max(1, tot // r.choice([1, 1, 7, 100, 5000]))) if r.random() < 0.9 else tot + 1
        return '%d %d\n%s\n' % (n, s, nums(a))

    def solve(d):
        t = ints(d); n, s = t[0], t[1]; p = [0]
        for x in t[2:2 + n]: p.append(p[-1] + x)
        best = n + 1
        for j in range(1, n + 1):
            i = bisect.bisect_right(p, p[j] - s, 0, j) - 1
            if i >= 0: best = min(best, j - i)
        return str(best if best <= n else -1)

    def brute(d):
        t = ints(d); n, s = t[0], t[1]; a = t[2:2 + n]; best = -1
        for i in range(n):
            for j in range(i + 1, n + 1):
                if sum(a[i:j]) >= s and (best < 0 or j - i < best): best = j - i
        return str(best)


@prob('b02_b_skip_day', 'Вычеркнуть день', 'training', ['Массивы', 'DP'], 50,
      r"Дана выручка чайханы за $n$ дней. Выберите непрерывный отрезок дней и, если хотите, вычеркните из него один день (например, день ремонта). После вычёркивания в отрезке должен остаться хотя бы один день. Какую наибольшую сумму оставшихся дней можно получить?",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ целых чисел $a_i$ ($|a_i| \le 10^4$).",
      r"Максимальная сумма.", ['5\n1 -2 0 3 -4\n', '3\n-1 -1 -1\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); hi = H(lv, 10 ** 4); b = r.choice([0, -hi // 3, hi // 4])
        return '%d\n%s\n' % (n, nums([max(-10 ** 4, min(10 ** 4, r.randint(-hi, hi) + b)) for _ in range(n)]))

    def solve(d):
        t = ints(d); a = t[1:1 + t[0]]; NEG = -10 ** 18
        f0 = a[0]; f1 = NEG; best = a[0]
        for x in a[1:]:
            f1 = max(f1 + x, f0); f0 = max(f0 + x, x)
            best = max(best, f0, f1)
        return str(best)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; best = max(a)
        for i in range(n):
            for j in range(i + 1, n):
                s = sum(a[i:j + 1])
                best = max(best, s, max(s - a[k] for k in range(i, j + 1)))
        return str(best)


@prob('b02_b_two_hikes', 'Два похода', 'training', ['Массивы', 'DP'], 40,
      r"Айгуль хочет совершить два похода по горным тропам: первый на $L$ дней подряд, второй на $M$ дней подряд, причём походы не пересекаются (порядок любой). За $i$-й день можно собрать $a_i$ ягод (может быть отрицательным: потери). Какая наибольшая суммарная выгода?",
      r"В первой строке $n$, $L$, $M$ ($1 \le L, M$, $L+M \le n \le 2 \cdot 10^5$). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Максимальная сумма.", ['6 1 2\n3 8 1 3 2 1\n'])
class _:
    def gen(r, lv):
        n = max(2, size(lv, BIG)); hi = H(lv, 10 ** 9)
        if r.random() < 0.5:
            l = r.randint(1, n - 1); m = r.randint(1, n - l)
        else:
            l = r.randint(1, min(5, n - 1)); m = r.randint(1, min(5, n - l))
        return '%d %d %d\n%s\n' % (n, l, m, nums([r.randint(-hi, hi) for _ in range(n)]))

    def solve(d):
        t = ints(d); n, l, m = t[:3]; a = t[3:3 + n]; p = [0]
        for x in a: p.append(p[-1] + x)
        W = [p[i + l] - p[i] for i in range(n - l + 1)]; V = [p[i + m] - p[i] for i in range(n - m + 1)]
        pre = V[:]; suf = V[:]
        for i in range(1, len(V)): pre[i] = max(pre[i], pre[i - 1])
        for i in range(len(V) - 2, -1, -1): suf[i] = max(suf[i], suf[i + 1])
        best = None
        for i in range(len(W)):
            if i + l < len(V):
                c = W[i] + suf[i + l]; best = c if best is None else max(best, c)
            if i - m >= 0:
                c = W[i] + pre[i - m]; best = c if best is None else max(best, c)
        return str(best)

    def brute(d):
        t = ints(d); n, l, m = t[:3]; a = t[3:3 + n]; best = None
        for i in range(n - l + 1):
            for j in range(n - m + 1):
                if i + l <= j or j + m <= i:
                    c = sum(a[i:i + l]) + sum(a[j:j + m])
                    if best is None or c > best: best = c
        return str(best)


@prob('b02_b_rotate_weights', 'Вращение в Чолпон-Ате', 'training', ['Массивы', 'Математика'], 40,
      r"На колесе обозрения в Чолпон-Ате $n$ кабинок, в $i$-й сидят $a_i$ человек. Колесо можно повернуть так, что последовательность циклически сдвинется. Для расположения $b_0, b_1, \dots, b_{n-1}$ определим вес $\sum i \cdot b_i$. Найдите наибольший вес среди всех $n$ циклических сдвигов.",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ целых чисел $a_i$ ($|a_i| \le 10^4$).",
      r"Максимальный вес.", ['4\n4 3 2 6\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); hi = H(lv, 10 ** 4)
        return '%d\n%s\n' % (n, nums([r.randint(-hi, hi) for _ in range(n)]))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; tot = sum(a); f = sum(i * x for i, x in enumerate(a)); best = f
        for k in range(n - 1):
            f = f - tot + n * a[k]; best = max(best, f)
        return str(best)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        return str(max(sum(i * a[(i + k) % n] for i in range(n)) for k in range(n)))


@prob('b02_b_best_square', 'Лучший квадрат поля', 'training', ['Массивы'], 30,
      r"Поле под Таласом разбито на клетки $n \times m$; в клетке $(i,j)$ ожидается прибыль $a_{ij}$. Нужно засеять квадрат $k \times k$. Какая наибольшая суммарная прибыль возможна?",
      r"В первой строке $n$, $m$, $k$ ($1 \le n \cdot m \le 2 \cdot 10^5$, $1 \le k \le \min(n,m)$). Далее $n$ строк по $m$ чисел $a_{ij}$ ($|a_{ij}| \le 10^4$).",
      r"Максимальная сумма.", ['3 3 2\n1 -2 3\n4 5 -6\n7 8 9\n'])
class _:
    def gen(r, lv):
        N = size(lv, BIG); hi = H(lv, 10 ** 4)
        n = max(1, min(N, int(N ** 0.5 * r.uniform(0.4, 2)))); m = max(1, N // n); mm = min(n, m)
        k = r.randint(1, mm) if r.random() < 0.5 else r.randint(1, min(mm, 4))
        g = [nums([r.randint(-hi, hi) for _ in range(m)]) for _ in range(n)]
        return '%d %d %d\n%s\n' % (n, m, k, '\n'.join(g))

    def solve(d):
        t = ints(d); n, m, k = t[:3]; v = t[3:]; p = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(n):
            row = 0
            for j in range(m):
                row += v[i * m + j]; p[i + 1][j + 1] = p[i][j + 1] + row
        best = None
        for i in range(k, n + 1):
            for j in range(k, m + 1):
                s = p[i][j] - p[i - k][j] - p[i][j - k] + p[i - k][j - k]
                if best is None or s > best: best = s
        return str(best)

    def brute(d):
        t = ints(d); n, m, k = t[:3]; v = t[3:]
        return str(max(sum(v[(i + x) * m + j + y] for x in range(k) for y in range(k))
                       for i in range(n - k + 1) for j in range(m - k + 1)))


@prob('b02_b_fence_karakol', 'Покраска забора в Караколе', 'training', ['Массивы', 'Жадные'], 18,
      r"Забор в Караколе состоит из $n$ досок, $i$-я должна получить $h_i$ слоёв краски. За один взмах кисти наносится один слой на несколько подряд идущих досок. Сколько взмахов потребуется как минимум?",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ целых чисел $h_i$ ($0 \le h_i \le 10^9$).",
      r"Минимальное число взмахов.", ['5\n2 1 3 3 0\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); hi = 4 if lv < 3 else 10 ** 9
        h = [r.randint(0, hi) for _ in range(n)]
        if lv > 4 and r.random() < 0.5:
            h = [0] * n; c = 0
            for i in range(n):
                c = max(0, min(10 ** 9, c + r.randint(-1000, 1000))); h[i] = c
        return '%d\n%s\n' % (n, nums(h))

    def solve(d):
        t = ints(d); prev = 0; res = 0
        for x in t[1:1 + t[0]]:
            res += max(0, x - prev); prev = x
        return str(res)

    def brute(d):
        t = ints(d); h = t[1:1 + t[0]]; res = 0
        for lay in range(1, max(h) + 1):
            prev = False
            for x in h:
                cur = x >= lay
                if cur and not prev: res += 1
                prev = cur
        return str(res)


@prob('b02_b_fest_yurts', 'Юрты на фестивале', 'training', ['Массивы'], 22,
      r"На фестивале в Бишкеке вдоль главной аллеи с точками $1, \dots, M$ расставлены $n$ юрт; $j$-я юрта закрывает от солнца точки от $l_j$ до $r_j$. Какое наибольшее число юрт одновременно закрывает одну точку и сколько точек закрыто именно таким числом юрт?",
      r"В первой строке $n$ и $M$ ($1 \le n, M \le 2 \cdot 10^5$). Далее $n$ строк с $l_j$ и $r_j$ ($1 \le l_j \le r_j \le M$).",
      r"Два числа: максимум и количество точек с этим значением.", ['3 6\n1 3\n2 4\n3 6\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); M = max(2, size(lv, BIG)); rows = []
        short = r.random() < 0.5
        for _ in range(n):
            l = r.randint(1, M)
            rr = min(M, l + r.randint(0, 5)) if short else r.randint(l, M)
            rows.append('%d %d' % (l, rr))
        return '%d %d\n%s\n' % (n, M, '\n'.join(rows))

    def solve(d):
        t = ints(d); n, M = t[0], t[1]; df = [0] * (M + 2)
        for i in range(n):
            df[t[2 + 2 * i]] += 1; df[t[3 + 2 * i] + 1] -= 1
        c = 0; mx = cnt = 0
        for i in range(1, M + 1):
            c += df[i]
            if c > mx: mx = c; cnt = 1
            elif c == mx: cnt += 1
        return '%d %d' % (mx, cnt)

    def brute(d):
        t = ints(d); n, M = t[0], t[1]
        cov = [sum(1 for i in range(n) if t[2 + 2 * i] <= x <= t[3 + 2 * i]) for x in range(1, M + 1)]
        return '%d %d' % (max(cov), cov.count(max(cov)))


@prob('b02_b_xor_cipher', 'Шифр Бакыта', 'training', ['Массивы', 'Математика'], 35,
      r"Бакыт зашифровал сообщение числами $a_1, \dots, a_n$. Ключом считается побитовое исключающее ИЛИ (xor) чисел на подряд идущем участке. Сколько участков дают в точности значение $K$?",
      r"В первой строке $n$ и $K$ ($1 \le n \le 2 \cdot 10^5$, $0 \le K < 2^{30}$). Во второй — $n$ чисел $a_i$ ($0 \le a_i < 2^{30}$).",
      r"Количество участков.", ['5 6\n4 2 2 6 0\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); b = 2 if lv < 3 else r.choice([2, 4, 10, 30]); a = [r.randrange(1 << b) for _ in range(n)]
        if r.random() < 0.7:
            i = r.randrange(n); j = r.randint(i, n - 1); k = 0
            for x in a[i:j + 1]: k ^= x
        else:
            k = r.randrange(1 << b)
        return '%d %d\n%s\n' % (n, k, nums(a))

    def solve(d):
        t = ints(d); n, k = t[0], t[1]; c = {0: 1}; s = res = 0
        for x in t[2:2 + n]:
            s ^= x; res += c.get(s ^ k, 0); c[s] = c.get(s, 0) + 1
        return str(res)

    def brute(d):
        t = ints(d); n, k = t[0], t[1]; a = t[2:2 + n]; res = 0
        for i in range(n):
            s = 0
            for j in range(i, n):
                s ^= a[j]
                if s == k: res += 1
        return str(res)


@prob('b02_b_three_pastures', 'Три равных пастбища', 'training', ['Массивы', 'Комбинаторика'], 30,
      r"Вдоль реки лежат $n$ участков, на $i$-м можно собрать $a_i$ ц сена (бывает и отрицательное значение: затраты). Участки нужно разрезать на три непустые части подряд так, чтобы суммы в частях совпали. Сколькими способами это можно сделать?",
      r"В первой строке $n$ ($3 \le n \le 2 \cdot 10^5$). Во второй — $n$ целых чисел $a_i$ ($|a_i| \le 10^4$).",
      r"Количество способов.", ['5\n1 2 3 0 3\n'])
class _:
    def gen(r, lv):
        n = max(3, size(lv, BIG)); hi = r.choice([1, 1, 2, 5]); a = [r.randint(-hi, hi) for _ in range(n)]
        a[-1] -= sum(a) % 3
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; tot = sum(a)
        if tot % 3: return '0'
        T = tot // 3; s = cnt = res = 0
        for j in range(n - 1):
            s += a[j]
            if s == 2 * T and j >= 1: res += cnt
            if s == T: cnt += 1
        return str(res)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        return str(sum(1 for i in range(1, n) for j in range(i + 1, n)
                       if sum(a[:i]) == sum(a[i:j]) == sum(a[j:])))


@prob('b02_b_bazaar_budget', 'Бюджет Нурлана на базаре', 'training', ['Сортировка', 'Двоичный поиск'], 22,
      r"На базаре в Оше продаются $n$ товаров с ценами $a_i$ сомов. У Нурлана $q$ планов: в $j$-м плане бюджет $b_j$. Какое наибольшее число разных товаров можно купить на $b_j$ сомов?",
      r"В первой строке $n$ и $q$ ($1 \le n, q \le 2 \cdot 10^5$). Во второй — $n$ цен $a_i$ ($1 \le a_i \le 10^9$). В третьей — $q$ бюджетов $b_j$ ($0 \le b_j \le 10^{14}$).",
      r"$q$ чисел через пробел.", ['4 3\n5 2 8 1\n0 3 10\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); q = size(lv, BIG); hi = 6 if lv < 3 else 10 ** 9
        a = [r.randint(1, hi) for _ in range(n)]; tot = sum(a)
        return '%d %d\n%s\n%s\n' % (n, q, nums(a), nums([r.randint(0, tot + 2) for _ in range(q)]))

    def solve(d):
        t = ints(d); n, q = t[0], t[1]; a = sorted(t[2:2 + n]); p = [0]
        for x in a: p.append(p[-1] + x)
        return nums([bisect.bisect_right(p, b) - 1 for b in t[2 + n:2 + n + q]])

    def brute(d):
        t = ints(d); n, q = t[0], t[1]; a = sorted(t[2:2 + n]); out = []
        for b in t[2 + n:2 + n + q]:
            c = 0
            for x in a:
                if b >= x:
                    b -= x; c += 1
                else:
                    break
            out.append(c)
        return nums(out)


@prob('b02_b_rain_then_ask', 'Дождь над арыками', 'training', ['Массивы', 'Структуры данных'], 38,
      r"Вдоль $n$ арыков в начале вода стоит на нуле. Сначала прошло $m$ дождей: $j$-й добавил $x_j$ единиц воды во все арыки с $l_j$ по $r_j$. После этого Чолпон задаёт $q$ вопросов: сколько всего воды в арыках с $u$ по $v$?",
      r"В первой строке $n$, $m$, $q$ ($1 \le n, m, q \le 2 \cdot 10^5$). Далее $m$ строк: $l_j$, $r_j$, $x_j$ ($1 \le l_j \le r_j \le n$, $0 \le x_j \le 10^4$). Далее $q$ строк: $u$, $v$ ($1 \le u \le v \le n$).",
      r"Для каждого вопроса — ответ на отдельной строке.", ['5 2 2\n1 3 2\n2 5 1\n1 5\n3 4\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); m = size(lv, BIG); q = size(lv, BIG); hi = H(lv, 10 ** 4)
        u = ['%d %d %d' % (l, rr, r.randint(0, hi)) for l, rr in segs(r, n, m, True)]
        qs = ['%d %d' % s for s in segs(r, n, q)]
        return '%d %d %d\n%s\n%s\n' % (n, m, q, '\n'.join(u), '\n'.join(qs))

    def solve(d):
        t = ints(d); n, m, q = t[:3]; df = [0] * (n + 2); o = t[3:]
        for i in range(m):
            l, rr, x = o[3 * i:3 * i + 3]; df[l] += x; df[rr + 1] -= x
        p = [0] * (n + 1); c = 0
        for i in range(1, n + 1):
            c += df[i]; p[i] = p[i - 1] + c
        o = o[3 * m:]
        return '\n'.join(str(p[o[2 * i + 1]] - p[o[2 * i] - 1]) for i in range(q))

    def brute(d):
        t = ints(d); n, m, q = t[:3]; a = [0] * n; o = t[3:]
        for i in range(m):
            l, rr, x = o[3 * i:3 * i + 3]
            for j in range(l - 1, rr): a[j] += x
        o = o[3 * m:]
        return '\n'.join(str(sum(a[o[2 * i] - 1:o[2 * i + 1]])) for i in range(q))


@prob('b02_b_greenhouse', 'Поливка теплицы', 'training', ['Массивы'], 45,
      r"Теплица Айгуль — таблица $n \times m$, сначала в каждой клетке 0 литров воды. Затем поливальщик $k$ раз добавляет $x$ литров во все клетки прямоугольника с углами $(r_1,c_1)$ и $(r_2,c_2)$. Выведите итоговую таблицу.",
      r"В первой строке $n$, $m$ и $k$ ($1 \le n \cdot m \le 2 \cdot 10^5$, $1 \le k \le 2 \cdot 10^5$). Далее $k$ строк: $r_1, c_1, r_2, c_2, x$ ($1 \le r_1 \le r_2 \le n$, $1 \le c_1 \le c_2 \le m$, $|x| \le 10^4$).",
      r"$n$ строк по $m$ чисел через пробел.", ['2 3 2\n1 1 2 2 5\n2 2 2 3 -1\n'])
class _:
    def gen(r, lv):
        N = size(lv, BIG); k = size(lv, BIG); hi = H(lv, 10 ** 4)
        n = max(1, min(N, int(N ** 0.5 * r.uniform(0.3, 2)))); m = max(1, N // n); rows = []
        for _ in range(k):
            r1 = r.randint(1, n); r2 = r.randint(r1, n); c1 = r.randint(1, m); c2 = r.randint(c1, m)
            rows.append('%d %d %d %d %d' % (r1, c1, r2, c2, r.randint(-hi, hi)))
        return '%d %d %d\n%s\n' % (n, m, k, '\n'.join(rows))

    def solve(d):
        t = ints(d); n, m, k = t[:3]; df = [[0] * (m + 2) for _ in range(n + 2)]; o = t[3:]
        for i in range(k):
            r1, c1, r2, c2, x = o[5 * i:5 * i + 5]
            df[r1][c1] += x; df[r1][c2 + 1] -= x; df[r2 + 1][c1] -= x; df[r2 + 1][c2 + 1] += x
        out = []
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                df[i][j] += df[i - 1][j] + df[i][j - 1] - df[i - 1][j - 1]
            out.append(nums(df[i][1:m + 1]))
        return '\n'.join(out)

    def brute(d):
        t = ints(d); n, m, k = t[:3]; g = [[0] * m for _ in range(n)]; o = t[3:]
        for i in range(k):
            r1, c1, r2, c2, x = o[5 * i:5 * i + 5]
            for a in range(r1 - 1, r2):
                for b in range(c1 - 1, c2): g[a][b] += x
        return '\n'.join(nums(row) for row in g)


@prob('b02_b_avg_norm', 'Прибыль не ниже нормы', 'training', ['Массивы', 'Структуры данных'], 55,
      r"Лавка Нурлана ежедневно приносит $a_i$ сомов. Назовём отрезок подряд идущих дней успешным, если среднедневная прибыль на нём не меньше нормы $X$. Сколько успешных отрезков?",
      r"В первой строке $n$ и $X$ ($1 \le n \le 2 \cdot 10^5$, $|X| \le 10^4$). Во второй — $n$ целых чисел $a_i$ ($|a_i| \le 10^4$).",
      r"Количество успешных отрезков.", ['4 2\n1 3 2 0\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); hi = H(lv, 10 ** 4); x = r.randint(-hi, hi) // 2
        return '%d %d\n%s\n' % (n, x, nums([r.randint(-hi, hi) for _ in range(n)]))

    def solve(d):
        t = ints(d); n, x = t[0], t[1]; p = [0]
        for v in t[2:2 + n]: p.append(p[-1] + v - x)
        rk = {v: i + 1 for i, v in enumerate(sorted(set(p)))}; m = len(rk) + 1; bit = [0] * (m + 1); res = 0
        for v in p:
            i = rk[v]; s = 0
            while i > 0: s += bit[i]; i &= i - 1
            res += s; i = rk[v]
            while i <= m: bit[i] += 1; i += i & -i
        return str(res)

    def brute(d):
        t = ints(d); n, x = t[0], t[1]; a = t[2:2 + n]
        return str(sum(1 for i in range(n) for j in range(i, n) if sum(a[i:j + 1]) >= x * (j - i + 1)))


@prob('b02_b_all_segments', 'Сумма всех отрезков урожая', 'training', ['Массивы', 'Математика', 'Комбинаторика'], 14,
      r"В ряд растут $n$ яблонь, с $i$-й собрали $a_i$ кг. Для каждого непрерывного участка деревьев посчитали сумму урожая, затем сложили все эти суммы. Найдите итог по модулю $10^9+7$.",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^9$).",
      r"Одно число.", ['3\n1 2 3\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); hi = H(lv, 10 ** 9)
        return '%d\n%s\n' % (n, nums([r.randint(0, hi) for _ in range(n)]))

    def solve(d):
        t = ints(d); n = t[0]
        return str(sum(x * (i + 1) * (n - i) for i, x in enumerate(t[1:1 + n])) % (10 ** 9 + 7))

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        return str(sum(sum(a[i:j + 1]) for i in range(n) for j in range(i, n)) % (10 ** 9 + 7))


@prob('b02_b_yurt_dist', 'Расстояния между юртами', 'training', ['Сортировка', 'Массивы'], 33,
      r"Юрты стоят вдоль дороги, координата $i$-й равна $a_i$. Для каждой юрты найдите суммарное расстояние до всех остальных юрт.",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ целых чисел $a_i$ ($|a_i| \le 10^9$).",
      r"$n$ чисел через пробел.", ['4\n1 5 2 9\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); hi = H(lv, 10 ** 9)
        return '%d\n%s\n' % (n, nums([r.randint(-hi, hi) for _ in range(n)]))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; o = sorted(range(n), key=a.__getitem__); res = [0] * n; tot = sum(a); pre = 0
        for k, i in enumerate(o):
            res[i] = a[i] * k - pre + (tot - pre - a[i]) - a[i] * (n - k - 1); pre += a[i]
        return nums(res)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        return nums([sum(abs(a[i] - y) for y in a) for i in range(n)])


@prob('b02_b_garland', 'Гирлянда на площади Ала-Тоо', 'training', ['Массивы'], 20,
      r"Вдоль площади Ала-Тоо висят $n$ ламп, сначала все выключены. Электрик $q$ раз переключает все лампы с $l$-й по $r$-ю (включённые гаснут, выключенные загораются). Сколько ламп горит в конце?",
      r"В первой строке $n$ и $q$ ($1 \le n, q \le 2 \cdot 10^5$). Далее $q$ строк: $l$ и $r$ ($1 \le l \le r \le n$).",
      r"Количество горящих ламп.", ['5 2\n1 3\n2 5\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); q = size(lv, BIG)
        return '%d %d\n%s\n' % (n, q, '\n'.join('%d %d' % s for s in segs(r, n, q, True)))

    def solve(d):
        t = ints(d); n, q = t[0], t[1]; df = [0] * (n + 2)
        for i in range(q):
            df[t[2 + 2 * i]] ^= 1; df[t[3 + 2 * i] + 1] ^= 1
        c = res = 0
        for i in range(1, n + 1):
            c ^= df[i]; res += c
        return str(res)

    def brute(d):
        t = ints(d); n, q = t[0], t[1]; a = [0] * n
        for i in range(q):
            for j in range(t[2 + 2 * i] - 1, t[3 + 2 * i]): a[j] ^= 1
        return str(sum(a))


@prob('b02_b_tail_zeros', 'Нули на конце', 'training', ['Математика', 'Массивы'], 28,
      r"В ряд выложены $n$ мешков с орехами, в $i$-м лежит $a_i$ кг. Для каждого из $q$ вопросов найдите, сколько нулей стоит в конце десятичной записи произведения масс мешков с $l$-го по $r$-й.",
      r"В первой строке $n$ и $q$ ($1 \le n, q \le 2 \cdot 10^5$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^9$). Далее $q$ строк: $l$ и $r$ ($1 \le l \le r \le n$).",
      r"Для каждого вопроса — ответ на отдельной строке.", ['4 2\n2 5 4 25\n1 2\n1 4\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); q = size(lv, BIG); hi = 12 if lv < 3 else 10 ** 9
        a = []
        for _ in range(n):
            v = r.randint(1, hi)
            if lv > 2 and r.random() < 0.4: v = max(1, v // 100) * r.choice([2, 4, 5, 25, 10])
            a.append(min(v, 10 ** 9))
        return '%d %d\n%s\n%s\n' % (n, q, nums(a), '\n'.join('%d %d' % s for s in segs(r, n, q)))

    def solve(d):
        t = ints(d); n, q = t[0], t[1]; p2 = [0]; p5 = [0]
        for x in t[2:2 + n]:
            c2 = c5 = 0
            while x % 2 == 0: x //= 2; c2 += 1
            while x % 5 == 0: x //= 5; c5 += 1
            p2.append(p2[-1] + c2); p5.append(p5[-1] + c5)
        o = t[2 + n:]
        return '\n'.join(str(min(p2[o[2 * i + 1]] - p2[o[2 * i] - 1], p5[o[2 * i + 1]] - p5[o[2 * i] - 1])) for i in range(q))

    def brute(d):
        t = ints(d); n, q = t[0], t[1]; a = t[2:2 + n]; o = t[2 + n:]; res = []
        for i in range(q):
            p = 1
            for x in a[o[2 * i] - 1:o[2 * i + 1]]: p *= x
            s = str(p); res.append(len(s) - len(s.rstrip('0')))
        return '\n'.join(map(str, res))


@prob('b02_b_rope_cut', 'Раздел верёвки Бакыта', 'training', ['Массивы', 'Жадные'], 12,
      r"Бакыт режет цепочку из $n$ грузов на две непустые части: левую (первые $k$ грузов) и правую. Он хочет, чтобы разность между весами частей по модулю была как можно меньше. Выведите эту наименьшую разность и наименьшее подходящее $k$.",
      r"В первой строке $n$ ($2 \le n \le 2 \cdot 10^5$). Во второй — $n$ целых чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Два числа: разность и $k$.", ['4\n3 1 4 1\n'])
class _:
    def gen(r, lv):
        n = max(2, size(lv, BIG)); hi = H(lv, 10 ** 9)
        return '%d\n%s\n' % (n, nums([r.randint(-hi, hi) for _ in range(n)]))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; tot = sum(a); pre = 0; best = None
        for k in range(1, n):
            pre += a[k - 1]; v = abs(2 * pre - tot)
            if best is None or v < best[0]: best = (v, k)
        return '%d %d' % best

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        return '%d %d' % min((abs(sum(a[:k]) - sum(a[k:])), k) for k in range(1, n))


@prob('b02_b_heavy_streak', 'Тяжёлая полоса', 'training', ['Массивы', 'Структуры данных'], 45,
      r"Нурлан записал, сколько часов он работал в каждый из $n$ дней. День считается тяжёлым, если работал больше 8 часов, иначе лёгким. Найдите длину самого длинного отрезка дней, на котором тяжёлых дней строго больше, чем лёгких (или 0, если такого нет).",
      r"В первой строке $n$ ($1 \le n \le 2 \cdot 10^5$). Во второй — $n$ целых чисел $a_i$ ($0 \le a_i \le 16$).",
      r"Длина отрезка.", ['6\n9 9 6 6 6 9\n', '2\n8 3\n'])
class _:
    def gen(r, lv):
        n = size(lv, BIG); p = r.choice([0.3, 0.5, 0.5, 0.7])
        return '%d\n%s\n' % (n, nums([r.randint(9, 16) if r.random() < p else r.randint(0, 8) for _ in range(n)]))

    def solve(d):
        t = ints(d); n = t[0]; p = [0]
        for x in t[1:1 + n]: p.append(p[-1] + (1 if x > 8 else -1))
        st = []
        for i in range(n + 1):
            if not st or p[i] < p[st[-1]]: st.append(i)
        best = 0
        for j in range(n, 0, -1):
            while st and p[st[-1]] < p[j]:
                best = max(best, j - st.pop())
        return str(best)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; best = 0
        for i in range(n):
            for j in range(i, n):
                seg = a[i:j + 1]
                if 2 * sum(1 for x in seg if x > 8) > len(seg): best = max(best, j - i + 1)
        return str(best)


@prob('b02_b_smooth_map', 'Сглаживание карты урожая', 'training', ['Массивы'], 40,
      r"Поле — таблица $n \times m$ с урожайностью $a_{ij}$. Для сглаживания в каждую клетку записывают сумму всех клеток, чьи номера строки и столбца отличаются от её собственных не более чем на $k$ (клетки за краем поля не считаются). Выведите новую таблицу.",
      r"В первой строке $n$, $m$ и $k$ ($1 \le n \cdot m \le 2 \cdot 10^5$, $0 \le k \le 2 \cdot 10^5$). Далее $n$ строк по $m$ чисел $a_{ij}$ ($|a_{ij}| \le 10^4$).",
      r"$n$ строк по $m$ чисел.", ['2 3 1\n1 2 3\n4 5 6\n'])
class _:
    def gen(r, lv):
        N = size(lv, BIG); hi = H(lv, 10 ** 4)
        n = max(1, min(N, int(N ** 0.5 * r.uniform(0.3, 2)))); m = max(1, N // n)
        k = r.choice([0, 1, 2, 5, 50, 10 ** 5]) if lv > 2 else r.randint(0, 3)
        g = [nums([r.randint(-hi, hi) for _ in range(m)]) for _ in range(n)]
        return '%d %d %d\n%s\n' % (n, m, k, '\n'.join(g))

    def solve(d):
        t = ints(d); n, m, k = t[:3]; v = t[3:]; p = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(n):
            row = 0
            for j in range(m):
                row += v[i * m + j]; p[i + 1][j + 1] = p[i][j + 1] + row
        out = []
        for i in range(n):
            r1 = max(0, i - k); r2 = min(n, i + k + 1); cur = []
            for j in range(m):
                c1 = max(0, j - k); c2 = min(m, j + k + 1)
                cur.append(p[r2][c2] - p[r1][c2] - p[r2][c1] + p[r1][c1])
            out.append(nums(cur))
        return '\n'.join(out)

    def brute(d):
        t = ints(d); n, m, k = t[:3]; v = t[3:]; out = []
        for i in range(n):
            out.append(nums([sum(v[x * m + y] for x in range(n) for y in range(m) if abs(x - i) <= k and abs(y - j) <= k) for j in range(m)]))
        return '\n'.join(out)
