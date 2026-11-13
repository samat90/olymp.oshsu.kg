import bisect
from collections import deque
from lib import prob, size, nums, ints

MOD = 10 ** 9 + 7


def arr(r, lv, big, lo, hi_small, hi_big):
    n = size(lv, big)
    h = hi_small if lv < 3 else hi_big
    return [r.randint(lo, h) for _ in range(n)]


@prob('carousel', 'Карусель юрт', 'training', ['Массивы'], 12,
      r"Юрты стоят по кругу, у $i$-й юрты номер $a_i$. Поворот карусели на $k$ шагов по часовой стрелке сдвигает все номера на $k$ позиций вправо, а вышедшие за конец возвращаются в начало. Выведите номера после поворота.",
      r"В первой строке $n$ и $k$ ($1 \le n \le 10^5$, $0 \le k \le 10^9$). Во второй — $n$ целых чисел $a_i$ ($|a_i| \le 10^9$).",
      r"$n$ чисел через пробел.", ['5 2\n1 2 3 4 5\n'])
class _:
    def gen(r, lv):
        a = arr(r, lv, 10 ** 5, -9, 9, 10 ** 9)
        return '%d %d\n%s\n' % (len(a), r.randint(0, 10 ** 9 if lv > 2 else 9), nums(a))

    def solve(d):
        t = ints(d); n, k = t[0], t[1] % t[0]; a = t[2:2 + n]
        return nums(a[n - k:] + a[:n - k])

    def brute(d):
        t = ints(d); n, k = t[0], t[1]; a = t[2:2 + n]
        for _ in range(k % n):
            a = [a[-1]] + a[:-1]
        return nums(a)


@prob('product_others', 'Произведение без себя', 'training', ['Массивы'], 30,
      r"Для каждой позиции $i$ найдите произведение всех чисел массива, кроме $a_i$, по модулю $10^9+7$. Делить нельзя: в массиве могут быть нули.",
      r"В первой строке $n$ ($2 \le n \le 10^5$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^9$).",
      r"$n$ чисел через пробел.", ['4\n1 2 3 4\n', '3\n0 5 0\n'])
class _:
    def gen(r, lv):
        a = arr(r, lv, 10 ** 5, 0, 4, 10 ** 9)
        a = a if len(a) > 1 else a + [1]
        if lv > 4 and lv % 3 == 0:
            a[r.randrange(len(a))] = 0
        return '%d\n%s\n' % (len(a), nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; pre = [1] * (n + 1)
        for i in range(n): pre[i + 1] = pre[i] * a[i] % MOD
        res = [0] * n; suf = 1
        for i in range(n - 1, -1, -1):
            res[i] = pre[i] * suf % MOD; suf = suf * a[i] % MOD
        return nums(res)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; out = []
        for i in range(n):
            p = 1
            for j in range(n):
                if j != i: p = p * a[j] % MOD
            out.append(p)
        return nums(out)


@prob('rain_gorge', 'Дождь в ущелье', 'olympiad', ['Массивы', 'Жадные'], 45,
      r"Дно ущелья разбито на $n$ столбцов шириной 1, высота $i$-го столбца $h_i$. После дождя вода задерживается между столбцами. Сколько единиц воды останется в ущелье?",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Во второй — $n$ целых чисел $h_i$ ($0 \le h_i \le 10^4$).",
      r"Количество воды.", ['12\n0 1 0 2 1 0 1 3 2 1 2 1\n'])
class _:
    def gen(r, lv):
        a = arr(r, lv, 10 ** 5, 0, 5, 10 ** 4)
        return '%d\n%s\n' % (len(a), nums(a))

    def solve(d):
        t = ints(d); a = t[1:1 + t[0]]; l, rr = 0, len(a) - 1; ml = mr = res = 0
        while l < rr:
            if a[l] < a[rr]:
                ml = max(ml, a[l]); res += ml - a[l]; l += 1
            else:
                mr = max(mr, a[rr]); res += mr - a[rr]; rr -= 1
        return str(res)

    def brute(d):
        t = ints(d); a = t[1:1 + t[0]]
        return str(sum(max(0, min(max(a[:i + 1]), max(a[i:])) - a[i]) for i in range(len(a))))


@prob('lake_walls', 'Озеро между скалами', 'training', ['Массивы', 'Жадные'], 34,
      r"На берегу стоят $n$ скал, $i$-я стоит в точке $i$ и имеет высоту $h_i$. Выберите две скалы $i < j$ и натяните между ними плотину: её площадь равна $(j - i) \cdot \min(h_i, h_j)$. Найдите наибольшую площадь.",
      r"В первой строке $n$ ($2 \le n \le 10^5$). Во второй — $n$ чисел $h_i$ ($0 \le h_i \le 10^9$).",
      r"Наибольшая площадь.", ['9\n1 8 6 2 5 4 8 3 7\n'])
class _:
    def gen(r, lv):
        a = arr(r, lv, 10 ** 5, 0, 9, 10 ** 9)
        a = a if len(a) > 1 else a + [3]
        return '%d\n%s\n' % (len(a), nums(a))

    def solve(d):
        t = ints(d); a = t[1:1 + t[0]]; i, j = 0, len(a) - 1; best = 0
        while i < j:
            best = max(best, (j - i) * min(a[i], a[j]))
            if a[i] < a[j]: i += 1
            else: j -= 1
        return str(best)

    def brute(d):
        t = ints(d); a = t[1:1 + t[0]]
        return str(max((j - i) * min(a[i], a[j]) for i in range(len(a)) for j in range(i + 1, len(a))))


@prob('triple_sum', 'Тройки подарков', 'olympiad', ['Массивы', 'Комбинаторика'], 52,
      r"Даны $n$ чисел $a_i$ и число $S$. Сколько существует троек индексов $i < j < k$, для которых $a_i + a_j + a_k = S$?",
      r"В первой строке $n$ и $S$ ($3 \le n \le 1500$, $|S| \le 3 \cdot 10^9$). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Количество троек.", ['5 6\n1 2 3 3 0\n'])
class _:
    def gen(r, lv):
        n = max(3, size(lv, 1500)); h = 4 if lv < 3 else (10 ** 9 if lv % 2 else 30)
        a = [r.randint(-h, h) for _ in range(n)]
        return '%d %d\n%s\n' % (n, sum(r.sample(a, 3)), nums(a))

    def solve(d):
        t = ints(d); n, s = t[0], t[1]; a = t[2:2 + n]; res = 0
        for k in range(2, n):
            cnt = {}
            for j in range(k):
                res += cnt.get(s - a[k] - a[j], 0)
                cnt[a[j]] = cnt.get(a[j], 0) + 1
        return str(res)

    def brute(d):
        t = ints(d); n, s = t[0], t[1]; a = t[2:2 + n]
        return str(sum(1 for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n) if a[i] + a[j] + a[k] == s))


@prob('apple_canal', 'Яблоки вдоль арыка', 'training', ['DP'], 28,
      r"Вдоль арыка растут $n$ яблонь, на $i$-й созрело $a_i$ яблок. Нельзя собирать с двух соседних яблонь. Какое наибольшее число яблок можно собрать?",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^4$).",
      r"Наибольшее число яблок.", ['4\n1 2 3 1\n', '5\n2 7 9 3 1\n'])
class _:
    def gen(r, lv):
        a = arr(r, lv, 10 ** 5, 0, 6, 10 ** 4)
        return '%d\n%s\n' % (len(a), nums(a))

    def solve(d):
        t = ints(d); p = q = 0
        for x in t[1:1 + t[0]]:
            p, q = q, max(q, p + x)
        return str(q)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; best = 0
        for m in range(1 << n):
            if m & (m >> 1): continue
            best = max(best, sum(a[i] for i in range(n) if m >> i & 1))
        return str(best)


@prob('stone_jumps', 'Прыжки по камням', 'training', ['Жадные', 'Массивы'], 30,
      r"Через горную реку лежат $n$ камней. Стоя на камне $i$, можно прыгнуть вперёд на любое число камней от $1$ до $a_i$ (при $a_i = 0$ стоять можно, но прыгнуть нельзя). Начинаем на первом камне. Можно ли добраться до последнего?",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^5$).",
      r"`YES` или `NO`.", ['5\n2 3 1 1 4\n', '5\n3 2 1 0 4\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); top = 3 if lv < 3 else r.choice([2, 3, 10, 100])
        a = [r.choice([0, 0, 1, 2, top]) if r.random() < 0.5 else r.randint(1, top) for _ in range(n)]
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; far = 0
        for i in range(n):
            if i > far: return 'NO'
            far = max(far, i + a[i])
        return 'YES'

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; seen = {0}; q = deque([0])
        while q:
            v = q.popleft()
            for u in range(v + 1, min(n - 1, v + a[v]) + 1):
                if u not in seen: seen.add(u); q.append(u)
        return 'YES' if n - 1 in seen else 'NO'


@prob('min_jumps', 'Кратчайший путь по камням', 'olympiad', ['Жадные', 'Массивы'], 42,
      r"Условия те же, что и в задаче «Прыжки по камням»: с камня $i$ можно прыгнуть вперёд на $1 \dots a_i$ камней. Теперь добраться до последнего камня гарантированно можно. За какое наименьшее число прыжков?",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^5$); до последнего камня можно добраться.",
      r"Наименьшее число прыжков.", ['5\n2 3 1 1 4\n', '1\n0\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); top = 3 if lv < 3 else r.choice([3, 10, 50])
        a = [r.randint(1, top) if r.random() < 0.8 else 0 for _ in range(n)]
        far = 0
        for i in range(n):  # make the last stone reachable
            if i > far:
                a[i - 1] = max(a[i - 1], 1) if far == i - 1 else a[i - 1]
                a[far] = max(a[far], i - far)
            far = max(far, i + a[i])
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; jumps = cur = far = 0
        for i in range(n - 1):
            far = max(far, i + a[i])
            if i == cur: jumps += 1; cur = far
        return str(jumps)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; f = [10 ** 9] * n; f[0] = 0
        for i in range(n):
            for u in range(i + 1, min(n - 1, i + a[i]) + 1):
                f[u] = min(f[u], f[i] + 1)
        return str(f[-1])


@prob('toi_halls', 'Залы для тоев', 'training', ['Сортировка', 'Жадные'], 36,
      r"Для $n$ тоев известно время начала $l_i$ и конца $r_i$ (полуинтервал $[l_i, r_i)$: если один той заканчивается в момент, когда другой начинается, зал можно использовать повторно). Какое наименьшее число залов понадобится?",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Далее $n$ строк с $l_i$, $r_i$ ($0 \le l_i < r_i \le 10^9$).",
      r"Наименьшее число залов.", ['3\n0 30\n5 10\n15 20\n', '2\n1 2\n2 3\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); hi = 15 if lv < 3 else 10 ** 9; seg = []
        for _ in range(n):
            l = r.randint(0, hi - 1); seg.append((l, min(hi, l + r.randint(1, 5 if lv < 3 else max(2, hi // n * 4)))))
        return '%d\n%s' % (n, ''.join('%d %d\n' % s for s in seg))

    def solve(d):
        t = ints(d); n = t[0]; ev = []
        for i in range(n): ev.append((t[1 + 2 * i], 1)); ev.append((t[2 + 2 * i], -1))
        ev.sort(); cur = best = 0
        for _, k in ev:
            cur += k; best = max(best, cur)
        return str(best)

    def brute(d):
        t = ints(d); n = t[0]; s = [(t[1 + 2 * i], t[2 + 2 * i]) for i in range(n)]
        return str(max(sum(1 for l, r_ in s if l <= x < r_) for x in range(0, 16)))


@prob('warmer_day', 'Когда потеплеет', 'training', ['Структуры данных', 'Массивы'], 36,
      r"Известна температура воздуха в Бишкеке на каждый из $n$ дней. Для каждого дня выведите, через сколько дней станет **строго теплее**, или $0$, если теплее уже не будет.",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Во второй — $n$ целых чисел $t_i$ ($-50 \le t_i \le 50$).",
      r"$n$ чисел через пробел.", ['8\n73 74 75 71 69 72 76 73\n'])
class _:
    def gen(r, lv):
        a = arr(r, lv, 10 ** 5, -4, 4, 50)
        return '%d\n%s\n' % (len(a), nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; res = [0] * n; st = []
        for i in range(n):
            while st and a[st[-1]] < a[i]:
                j = st.pop(); res[j] = i - j
            st.append(i)
        return nums(res)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        return nums([next((j - i for j in range(i + 1, n) if a[j] > a[i]), 0) for i in range(n)])


@prob('felt_histogram', 'Узор из прямоугольников', 'olympiad', ['Структуры данных', 'Массивы'], 55,
      r"Полоса кошмы состоит из $n$ вертикальных столбцов шириной 1 и высотой $h_i$. Найдите наибольшую площадь прямоугольника со сторонами по линиям сетки, целиком лежащего внутри полосы.",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Во второй — $n$ чисел $h_i$ ($0 \le h_i \le 10^9$).",
      r"Наибольшая площадь.", ['6\n2 1 5 6 2 3\n'])
class _:
    def gen(r, lv):
        a = arr(r, lv, 10 ** 5, 0, 6, 10 ** 9)
        return '%d\n%s\n' % (len(a), nums(a))

    def solve(d):
        t = ints(d); a = t[1:1 + t[0]] + [0]; st = []; best = 0
        for i, x in enumerate(a):
            s = i
            while st and st[-1][1] >= x:
                s, h = st.pop(); best = max(best, h * (i - s))
            st.append((s, x))
        return str(best)

    def brute(d):
        t = ints(d); a = t[1:1 + t[0]]
        return str(max(min(a[i:j + 1]) * (j - i + 1) for i in range(len(a)) for j in range(i, len(a))))


@prob('shepherd_speed', 'Скорость чабана', 'training', ['Двоичный поиск'], 38,
      r"У чабана $n$ отар, в $i$-й отаре $a_i$ овец. За час он может перегнать на новое пастбище не более $k$ овец одной отары (если в отаре меньше $k$ овец, час всё равно тратится целиком на неё). За $H$ часов нужно перегнать все отары. Найдите наименьшее целое $k$, при котором это возможно.",
      r"В первой строке $n$ и $H$ ($1 \le n \le 10^5$, $n \le H \le 10^9$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"Наименьшее $k$.", ['4 8\n3 6 7 11\n'])
class _:
    def gen(r, lv):
        a = arr(r, lv, 10 ** 5, 1, 12, 10 ** 9); n = len(a)
        return '%d %d\n%s\n' % (n, r.randint(n, n * 5 if lv < 5 else 10 ** 9), nums(a))

    def solve(d):
        t = ints(d); n, h = t[0], t[1]; a = t[2:2 + n]; lo, hi = 1, max(a)
        while lo < hi:
            m = (lo + hi) // 2
            if sum((x + m - 1) // m for x in a) <= h: hi = m
            else: lo = m + 1
        return str(lo)

    def brute(d):
        t = ints(d); n, h = t[0], t[1]; a = t[2:2 + n]
        return str(next(k for k in range(1, max(a) + 1) if sum((x + k - 1) // k for x in a) <= h))


@prob('route_parts', 'Этапы марафона', 'olympiad', ['Двоичный поиск', 'Жадные'], 55,
      r"Марафонская трасса состоит из $n$ участков длиной $a_i$ км. Её нужно разбить на $m$ этапов из подряд идущих участков (каждый этап непустой). Длиной этапа считается сумма его участков. Как разбить трассу, чтобы самый длинный этап был как можно короче? Выведите его длину.",
      r"В первой строке $n$ и $m$ ($1 \le m \le n \le 10^5$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^4$).",
      r"Минимально возможная длина самого длинного этапа.", ['5 2\n7 2 5 10 8\n'])
class _:
    def gen(r, lv):
        a = arr(r, lv, 10 ** 5, 1, 9, 10 ** 4); n = len(a)
        return '%d %d\n%s\n' % (n, r.randint(1, n), nums(a))

    def solve(d):
        t = ints(d); n, m = t[0], t[1]; a = t[2:2 + n]; lo, hi = max(a), sum(a)
        while lo < hi:
            mid = (lo + hi) // 2; parts = 1; cur = 0
            for x in a:
                if cur + x > mid: parts += 1; cur = x
                else: cur += x
            if parts <= m: hi = mid
            else: lo = mid + 1
        return str(lo)

    def brute(d):
        t = ints(d); n, m = t[0], t[1]; a = t[2:2 + n]; INF = 10 ** 18
        f = [[INF] * (m + 1) for _ in range(n + 1)]; f[0][0] = 0
        for i in range(1, n + 1):
            for k in range(1, m + 1):
                for j in range(i):
                    if f[j][k - 1] < INF:
                        f[i][k] = min(f[i][k], max(f[j][k - 1], sum(a[j:i])))
        return str(f[n][m])


@prob('shifted_ridge', 'Сдвинутый хребет', 'training', ['Двоичный поиск'], 40,
      r"Высоты вершин хребта были записаны по возрастанию (все различны), а потом список циклически сдвинули: например, $4\ 5\ 6\ 1\ 2\ 3$. Для $q$ запросов определите позицию вершины заданной высоты (нумерация с 1) или выведите $-1$.",
      r"В первой строке $n$ и $q$ ($1 \le n, q \le 10^5$). Во второй — $n$ различных чисел $a_i$ (сдвинутая возрастающая последовательность, $|a_i| \le 10^9$). В третьей — $q$ запрашиваемых высот $x_j$ ($|x_j| \le 10^9$).",
      r"$q$ чисел, по одному в строке.", ['6 3\n4 5 6 1 2 3\n6 1 7\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); q = size(lv, 10 ** 5)
        hi = 20 if lv < 3 else 10 ** 9
        base = sorted(r.sample(range(-hi, hi), n)); k = r.randrange(n)
        a = base[k:] + base[:k]
        xs = [r.choice(a) if r.random() < 0.6 else r.randint(-hi, hi) for _ in range(q)]
        return '%d %d\n%s\n%s\n' % (n, q, nums(a), nums(xs))

    def solve(d):
        t = ints(d); n, q = t[0], t[1]; a = t[2:2 + n]; xs = t[2 + n:2 + n + q]
        k = a.index(min(a)) if False else next((i for i in range(1, n) if a[i] < a[i - 1]), 0)
        # binary search the rotation point instead of scanning
        lo, hi = 0, n - 1
        while lo < hi:
            m = (lo + hi) // 2
            if a[m] > a[hi]: lo = m + 1
            else: hi = m
        k = lo; s = a[k:] + a[:k]; out = []
        for x in xs:
            i = bisect.bisect_left(s, x)
            out.append(str((i + k) % n + 1) if i < n and s[i] == x else '-1')
        return '\n'.join(out)

    def brute(d):
        t = ints(d); n, q = t[0], t[1]; a = t[2:2 + n]
        return '\n'.join(str(a.index(x) + 1) if x in a else '-1' for x in t[2 + n:2 + n + q])


@prob('first_last', 'Первый и последний', 'training', ['Двоичный поиск'], 26,
      r"В отсортированном по неубыванию списке цен на кумыс найдите для каждого из $q$ запросов номер первого и номер последнего вхождения числа $x$ (нумерация с 1). Если числа нет, выведите `-1 -1`.",
      r"В первой строке $n$ и $q$ ($1 \le n, q \le 10^5$). Во второй — $n$ чисел по неубыванию ($0 \le a_i \le 10^9$). В третьей — $q$ чисел $x_j$ ($0 \le x_j \le 10^9$).",
      r"$q$ строк по два числа.", ['6 3\n1 2 2 2 5 7\n2 5 3\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); q = size(lv, 10 ** 5); hi = 6 if lv < 3 else 10 ** (3 + lv % 7)
        a = sorted(r.randint(0, hi) for _ in range(n))
        xs = [r.choice(a) if r.random() < 0.6 else r.randint(0, hi + 1) for _ in range(q)]
        return '%d %d\n%s\n%s\n' % (n, q, nums(a), nums(xs))

    def solve(d):
        t = ints(d); n, q = t[0], t[1]; a = t[2:2 + n]; out = []
        for x in t[2 + n:2 + n + q]:
            l = bisect.bisect_left(a, x); r_ = bisect.bisect_right(a, x)
            out.append('%d %d' % (l + 1, r_) if l < r_ else '-1 -1')
        return '\n'.join(out)

    def brute(d):
        t = ints(d); n, q = t[0], t[1]; a = t[2:2 + n]; out = []
        for x in t[2 + n:2 + n + q]:
            idx = [i + 1 for i in range(n) if a[i] == x]
            out.append('%d %d' % (idx[0], idx[-1]) if idx else '-1 -1')
        return '\n'.join(out)


@prob('candies_line', 'Конфеты на празднике', 'olympiad', ['Жадные', 'Массивы'], 48,
      r"В очереди стоят $n$ детей, у $i$-го оценка $r_i$ за поделку. Каждому нужно дать хотя бы одну конфету, а ребёнок с оценкой строго выше, чем у соседа (слева или справа), должен получить конфет строго больше этого соседа. Какое наименьшее общее число конфет понадобится?",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Во второй — $n$ чисел $r_i$ ($1 \le r_i \le 10^9$).",
      r"Наименьшее число конфет.", ['3\n1 0 2\n'.replace('0', '3')])
class _:
    def gen(r, lv):
        a = arr(r, lv, 10 ** 5, 1, 4, 10 ** 9 if lv % 2 else 6)
        return '%d\n%s\n' % (len(a), nums(a))

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


@prob('hunter_arrows', 'Стрелы охотника', 'training', ['Жадные', 'Сортировка'], 40,
      r"Охотник стреляет вертикально вверх из точки $x$ оси: стрела поражает все мишени-отрезки $[l_i, r_i]$ (концы включены), которые содержат $x$. Какое наименьшее число стрел нужно, чтобы поразить все $n$ мишеней?",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Далее $n$ строк с $l_i$, $r_i$ ($0 \le l_i \le r_i \le 10^9$).",
      r"Наименьшее число стрел.", ['4\n1 6\n2 8\n7 12\n10 16\n', '2\n1 2\n3 4\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); hi = 11 if lv < 3 else 10 ** 9; seg = []
        for _ in range(n):
            l = r.randint(0, hi); seg.append((l, min(hi, l + r.randint(0, 4 if lv < 3 else max(1, hi // n * 3)))))
        return '%d\n%s' % (n, ''.join('%d %d\n' % s for s in seg))

    def solve(d):
        t = ints(d); n = t[0]; s = sorted((t[2 + 2 * i], t[1 + 2 * i]) for i in range(n)); cnt = 0; last = -1
        for r_, l in s:
            if l > last: cnt += 1; last = r_
        return str(cnt)

    def brute(d):
        t = ints(d); n = t[0]; s = [(t[1 + 2 * i], t[2 + 2 * i]) for i in range(n)]
        best = n
        for m in range(1 << 12):
            if bin(m).count('1') >= best: continue
            if all(any(m >> x & 1 for x in range(l, r_ + 1)) for l, r_ in s): best = bin(m).count('1')
        return str(best)


@prob('fuel_route', 'Заправки на трассе Бишкек — Ош', 'training', ['Жадные', 'Массивы'], 36,
      r"На кольцевой трассе стоят $n$ заправок. На $i$-й можно взять $g_i$ литров, а до следующей заправки ехать $c_i$ литров. Бак пуст, вместимость не ограничена. С какой заправки нужно начать, чтобы проехать полный круг? Если подходящих несколько, выведите наименьший номер; если нет ни одной — $-1$. Нумерация с 1.",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Далее $n$ строк с $g_i$, $c_i$ ($0 \le g_i, c_i \le 10^4$).",
      r"Номер заправки или $-1$.", ['5\n1 3\n2 4\n3 5\n4 1\n5 2\n', '2\n2 3\n2 3\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); hi = 5 if lv < 3 else 10 ** 4
        g = [r.randint(0, hi) for _ in range(n)]; c = [max(0, x + r.randint(-hi // 3, hi // 3)) for x in g]
        if r.random() < 0.7: c[r.randrange(n)] = 0
        diff = sum(c) - sum(g)
        if r.random() < 0.8 and diff > 0: g[r.randrange(n)] += diff
        return '%d\n%s' % (n, ''.join('%d %d\n' % x for x in zip(g, c)))

    def solve(d):
        t = ints(d); n = t[0]; tot = cur = 0; start = 0
        for i in range(n):
            x = t[1 + 2 * i] - t[2 + 2 * i]; tot += x; cur += x
            if cur < 0: cur = 0; start = i + 1
        return str(start + 1) if tot >= 0 else '-1'

    def brute(d):
        t = ints(d); n = t[0]
        for s in range(n):
            f = 0; ok = True
            for k in range(n):
                i = (s + k) % n; f += t[1 + 2 * i] - t[2 + 2 * i]
                if f < 0: ok = False; break
            if ok: return str(s + 1)
        return '-1'


@prob('majority_vote', 'Голосование в айыл окмоту', 'training', ['Массивы'], 20,
      r"В голосовании участвовали $n$ человек, $i$-й проголосовал за кандидата $a_i$. Победитель должен набрать **больше половины** голосов. Выведите номер победителя или $-1$, если такого нет.",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"Номер кандидата или $-1$.", ['5\n3 2 3 3 1\n', '4\n1 1 2 2\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); k = 3 if lv < 3 else r.choice([2, 5, 1000]); w = r.randint(1, k)
        p = r.choice([0.3, 0.55, 0.8])
        a = [w if r.random() < p else r.randint(1, k) for _ in range(n)]
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; cand = None; c = 0
        for x in a:
            if c == 0: cand, c = x, 1
            elif x == cand: c += 1
            else: c -= 1
        return str(cand) if a.count(cand) * 2 > n else '-1'

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        return str(next((x for x in set(a) if a.count(x) * 2 > n), -1))


@prob('lost_yurt', 'Пропавшая юрта', 'training', ['Математика', 'Массивы'], 14,
      r"В ряду должны стоять юрты с номерами $0, 1, \dots, n$, но одну убрали. Даны номера оставшихся $n$ юрт в произвольном порядке. Найдите номер убранной.",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Во второй — $n$ различных чисел от $0$ до $n$.",
      r"Номер убранной юрты.", ['3\n3 0 1\n'])
class _:
    def gen(r, lv):
        n = max(1, size(lv, 10 ** 5)); a = list(range(n + 1)); r.shuffle(a); a.pop()
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; return str(n * (n + 1) // 2 - sum(t[1:1 + n]))

    def brute(d):
        t = ints(d); n = t[0]; return str(next(x for x in range(n + 1) if x not in set(t[1:1 + n])))


@prob('odd_one_out', 'Одинокая овца', 'training', ['Математика', 'Массивы'], 16,
      r"В отаре у каждой овцы, кроме одной, есть пара с тем же номером бирки. Найдите номер бирки одинокой овцы.",
      r"В первой строке $n$ — нечётное число ($1 \le n \le 10^5 + 1$). Во второй — $n$ чисел ($1 \le a_i \le 10^9$): каждое число встречается дважды, кроме одного.",
      r"Номер бирки одинокой овцы.", ['5\n4 1 2 1 2\n'])
class _:
    def gen(r, lv):
        m = max(1, size(lv, 50000)); hi = 10 if lv < 3 else 10 ** 9
        vals = r.sample(range(1, hi + 1), min(hi, m + 1)); lone = vals.pop(); vals = vals[:m]
        a = [lone] + vals * 2; r.shuffle(a)
        return '%d\n%s\n' % (len(a), nums(a))

    def solve(d):
        t = ints(d); x = 0
        for v in t[1:1 + t[0]]: x ^= v
        return str(x)

    def brute(d):
        t = ints(d); a = t[1:1 + t[0]]; return str(next(v for v in a if a.count(v) == 1))
