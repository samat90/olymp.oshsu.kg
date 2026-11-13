import math
from collections import deque, Counter
from functools import lru_cache
from lib import prob, size, nums, ints

MOD = 10 ** 9 + 7


def word(r, n, alpha):
    return ''.join(r.choice(alpha) for _ in range(n))


def matrix(r, lv, big, hi=9):
    n = r.randint(1, 4) if lv < 3 else size(lv, big)
    return n, [[r.randint(1, hi if lv < 3 else 10 ** 9) for _ in range(n)] for _ in range(n)]


@prob('carpet_turn', 'Поворот ковра', 'training', ['Массивы', 'Реализация'], 16,
      r"Квадратный ковёр размера $n \times n$ с числами-узорами повернули на $90^\circ$ **по часовой стрелке**. Выведите, как он выглядит теперь.",
      r"В первой строке $n$ ($1 \le n \le 500$). Далее $n$ строк по $n$ чисел ($1 \le a_{ij} \le 10^9$).",
      r"$n$ строк по $n$ чисел.", ['3\n1 2 3\n4 5 6\n7 8 9\n'])
class _:
    def gen(r, lv):
        n, m = matrix(r, lv, 500)
        return '%d\n%s' % (n, ''.join(nums(x) + '\n' for x in m))

    def solve(d):
        t = ints(d); n = t[0]; m = [t[1 + i * n:1 + (i + 1) * n] for i in range(n)]
        return '\n'.join(nums(list(row)) for row in zip(*m[::-1]))

    def brute(d):
        t = ints(d); n = t[0]; m = [t[1 + i * n:1 + (i + 1) * n] for i in range(n)]
        return '\n'.join(nums([m[n - 1 - j][i] for j in range(n)]) for i in range(n))


@prob('spiral_pattern', 'Спираль узора', 'training', ['Массивы', 'Реализация'], 26,
      r"Выпишите элементы таблицы $h \times w$ по спирали: начиная с левого верхнего угла вправо, затем вниз, влево и вверх, закручиваясь к центру.",
      r"В первой строке $h$ и $w$ ($1 \le h, w \le 500$). Далее $h$ строк по $w$ чисел ($1 \le a_{ij} \le 10^9$).",
      r"Все $hw$ чисел в порядке обхода через пробел.", ['3 3\n1 2 3\n4 5 6\n7 8 9\n', '2 3\n1 2 3\n4 5 6\n'])
class _:
    def gen(r, lv):
        h = r.randint(1, 4) if lv < 3 else size(lv, 500); w = r.randint(1, 4) if lv < 3 else size(lv, 500)
        hi = 9 if lv < 3 else 10 ** 9
        return '%d %d\n%s' % (h, w, ''.join(nums([r.randint(1, hi) for _ in range(w)]) + '\n' for _ in range(h)))

    def solve(d):
        t = ints(d); h, w = t[:2]; m = [t[2 + i * w:2 + (i + 1) * w] for i in range(h)]; out = []
        top, bot, left, right = 0, h - 1, 0, w - 1
        while top <= bot and left <= right:
            out += m[top][left:right + 1]; top += 1
            out += [m[i][right] for i in range(top, bot + 1)]; right -= 1
            if top <= bot: out += m[bot][left:right + 1][::-1]; bot -= 1
            if left <= right: out += [m[i][left] for i in range(bot, top - 1, -1)]; left += 1
        return nums(out)

    def brute(d):
        t = ints(d); h, w = t[:2]; m = [t[2 + i * w:2 + (i + 1) * w] for i in range(h)]
        seen = [[False] * w for _ in range(h)]; x = y = 0; dx, dy = 0, 1; out = []
        for _ in range(h * w):
            out.append(m[x][y]); seen[x][y] = True
            nx, ny = x + dx, y + dy
            if not (0 <= nx < h and 0 <= ny < w) or seen[nx][ny]:
                dx, dy = dy, -dx; nx, ny = x + dx, y + dy
            x, y = nx, ny
        return nums(out)


@prob('mirror_number', 'Зеркальное число', 'training', ['Математика', 'Реализация'], 8,
      r"Запишите цифры числа в обратном порядке. Знак сохраняется, нули в начале результата отбрасываются.",
      r"Одно целое число $n$ ($|n| \le 10^{18}$).",
      r"Число с цифрами в обратном порядке.", ['123\n', '-120\n'])
class _:
    def gen(r, lv):
        n = r.randint(-30, 30) if lv < 3 else r.randint(-10 ** (lv * 2), 10 ** (min(18, lv * 2)))
        return '%d\n' % (n * 10 if lv % 3 == 0 and lv > 2 else n)

    def solve(d):
        n = int(d.split()[0]); s = int(str(abs(n))[::-1]); return str(-s if n < 0 else s)

    def brute(d):
        n = int(d.split()[0]); a = abs(n); r_ = 0
        while a: r_ = r_ * 10 + a % 10; a //= 10
        return str(-r_ if n < 0 else r_)


@prob('palin_tickets', 'Билеты-перевёртыши', 'olympiad', ['Математика'], 50,
      r"Номер билета называют перевёртышем, если он читается одинаково слева направо и справа налево (без ведущих нулей). Сколько номеров-перевёртышей среди чисел от $l$ до $r$ включительно?",
      r"Одна строка: $l$ и $r$ ($1 \le l \le r \le 10^{12}$).",
      r"Количество чисел-палиндромов.", ['1 100\n', '120 130\n'])
class _:
    def gen(r, lv):
        hi = 10 ** (lv + 1) if lv < 3 else 10 ** (lv + 4 if lv < 8 else 12)
        l = r.randint(1, hi); return '%d %d\n' % (l, r.randint(l, hi))

    def solve(d):
        l, r_ = ints(d)[:2]
        def upto(n):
            if n <= 0: return 0
            s = str(n); L = len(s); tot = sum(9 * 10 ** ((k - 1) // 2) for k in range(1, L))
            half = s[:(L + 1) // 2]; cnt = int(half) - 10 ** ((L + 1) // 2 - 1)
            pal = half + half[:L // 2][::-1]
            return tot + cnt + (1 if int(pal) <= n else 0)
        return str(upto(r_) - upto(l - 1))

    def brute(d):
        l, r_ = ints(d)[:2]; return str(sum(1 for x in range(l, r_ + 1) if str(x) == str(x)[::-1]))


@prob('happy_days', 'Счастливые дни', 'training', ['Математика', 'Реализация'], 30,
      r"Число называется счастливым, если, заменяя его раз за разом суммой квадратов его цифр, мы в итоге придём к $1$ (например, $19 \to 82 \to 68 \to 100 \to 1$). Сколько счастливых чисел среди $1, 2, \dots, n$?",
      r"Одно число $n$ ($1 \le n \le 10^6$).",
      r"Количество счастливых чисел.", ['20\n', '1\n'])
class _:
    def gen(r, lv):
        return '%d\n' % (r.randint(1, 40) if lv < 3 else [10 ** 3, 10 ** 4, 10 ** 5, 3 * 10 ** 5, 6 * 10 ** 5, 10 ** 6, 999999][min(6, lv - 3)] - r.randint(0, 9))

    def solve(d):
        n = int(d.split()[0]); cache = {1: True}
        def nxt(x): return sum(int(c) ** 2 for c in str(x))
        sq = [i * i for i in range(10)]
        ok = bytearray(n + 1)
        small = {}
        def happy(x):
            seen = set()
            while x != 1 and x not in seen: seen.add(x); x = nxt(x)
            return x == 1
        mx = 81 * len(str(n)) + 1; hp = [happy(x) if x else False for x in range(mx + 1)]
        cnt = 0
        for x in range(1, n + 1):
            y = x; s = 0
            while y: s += sq[y % 10]; y //= 10
            if hp[s] if s <= mx else happy(s): cnt += 1
        return str(cnt)

    def brute(d):
        n = int(d.split()[0]); cnt = 0
        for x in range(1, n + 1):
            seen = set()
            while x != 1 and x not in seen: seen.add(x); x = sum(int(c) ** 2 for c in str(x))
            cnt += x == 1
        return str(cnt)


@prob('long_product', 'Умножение в столбик', 'training', ['Математика', 'Реализация'], 28,
      r"Перемножьте два очень больших неотрицательных числа.",
      r"В двух строках записаны числа $a$ и $b$ без ведущих нулей, не более 1000 цифр каждое.",
      r"Их произведение.", ['12\n34\n', '0\n999\n'])
class _:
    def gen(r, lv):
        def num(n): return '0' if n == 0 else str(r.randint(1, 9)) + word(r, n - 1, '0123456789')
        return num(r.randint(0, 3) if lv < 3 else size(lv, 1000)) + '\n' + num(r.randint(0, 3) if lv < 3 else size(lv, 1000)) + '\n'

    def solve(d):
        a, b = d.split()[:2]; res = [0] * (len(a) + len(b))
        for i, x in enumerate(reversed(a)):
            for j, y in enumerate(reversed(b)): res[i + j] += int(x) * int(y)
        c = 0
        for k in range(len(res)):
            c += res[k]; res[k] = c % 10; c //= 10
        s = ''.join(map(str, reversed(res))).lstrip('0'); return s or '0'

    def brute(d):
        a, b = d.split()[:2]; return str(int(a) * int(b))


@prob('square_field', 'Квадрат поля', 'training', ['Двоичный поиск', 'Математика'], 24,
      r"Поле площади $n$ м² хотят огородить квадратным забором наибольшей возможной стороны так, чтобы квадрат поместился в поле по площади. Найдите наибольшее целое $k$, для которого $k^2 \le n$.",
      r"Одно число $n$ ($0 \le n \le 10^{18}$).",
      r"Целая часть квадратного корня из $n$.", ['17\n', '0\n'])
class _:
    def gen(r, lv):
        n = r.randint(0, 50) if lv < 3 else r.randint(0, 10 ** 18) // 10 ** (9 - lv)
        if lv > 4 and lv % 2: k = r.randint(1, 10 ** 9 - 1); n = k * k - r.choice([0, 1])
        return '%d\n' % n

    def solve(d):
        n = int(d.split()[0]); lo, hi = 0, 10 ** 9 + 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if m * m <= n: lo = m
            else: hi = m
        return str(lo)

    def brute(d):
        return str(math.isqrt(int(d.split()[0])))


@prob('bowl_stack', 'Стопка мисок', 'training', ['Структуры данных'], 28,
      r"Мастер складывает в стопку миски с номерами-размерами. Операции: `push x` — положить миску размера $x$ сверху; `pop` — снять верхнюю; `min` — вывести наименьший размер в стопке. Операции `pop` и `min` выполняются только при непустой стопке.",
      r"В первой строке $q$ ($1 \le q \le 10^5$). Далее $q$ строк с операциями, $|x| \le 10^9$.",
      r"Для каждой операции `min` — ответ в отдельной строке.", ['5\npush 3\npush 1\nmin\npop\nmin\n'])
class _:
    def gen(r, lv):
        q = size(lv, 10 ** 5); ops = []; sz = 0; hi = 6 if lv < 3 else 10 ** 9
        for _ in range(q):
            c = r.random()
            if sz == 0 or c < 0.5: ops.append('push %d' % r.randint(-hi, hi)); sz += 1
            elif c < 0.75: ops.append('pop'); sz -= 1
            else: ops.append('min')
        ops.append('min') if sz else None
        return '%d\n%s\n' % (len(ops), '\n'.join(ops))

    def solve(d):
        t = d.split('\n'); q = int(t[0]); st = []; out = []
        for line in t[1:1 + q]:
            if line.startswith('push'):
                x = int(line.split()[1]); st.append(min(x, st[-1]) if st else x)
            elif line == 'pop': st.pop()
            else: out.append(str(st[-1]))
        return '\n'.join(out)

    def brute(d):
        t = d.split('\n'); q = int(t[0]); st = []; out = []
        for line in t[1:1 + q]:
            if line.startswith('push'): st.append(int(line.split()[1]))
            elif line == 'pop': st.pop()
            else: out.append(str(min(st)))
        return '\n'.join(out)


@prob('pass_window', 'Окно на перевале', 'olympiad', ['Структуры данных', 'Массивы'], 44,
      r"Дан массив высот $a_1, \dots, a_n$. Окно ширины $k$ сдвигается слева направо. Для каждого положения окна выведите максимальную высоту внутри него.",
      r"В первой строке $n$ и $k$ ($1 \le k \le n \le 10^5$). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"$n-k+1$ чисел через пробел.", ['8 3\n1 3 -1 -3 5 3 6 7\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); hi = 6 if lv < 3 else 10 ** 9; a = [r.randint(-hi, hi) for _ in range(n)]
        if lv > 4 and lv % 3 == 0: a.sort()
        return '%d %d\n%s\n' % (n, r.randint(1, n), nums(a))

    def solve(d):
        t = ints(d); n, k = t[:2]; a = t[2:2 + n]; dq = deque(); out = []
        for i, x in enumerate(a):
            while dq and a[dq[-1]] <= x: dq.pop()
            dq.append(i)
            if dq[0] <= i - k: dq.popleft()
            if i >= k - 1: out.append(a[dq[0]])
        return nums(out)

    def brute(d):
        t = ints(d); n, k = t[:2]; a = t[2:2 + n]
        return nums([max(a[i:i + k]) for i in range(n - k + 1)])


@prob('top_numbers', 'Самые частые номера', 'training', ['Сортировка', 'Структуры данных'], 22,
      r"Среди $n$ номеров найдите $k$ самых частых. Если у нескольких номеров одинаковая частота, раньше идёт меньший номер.",
      r"В первой строке $n$ и $k$ ($1 \le n \le 10^5$, $1 \le k \le$ числа различных номеров). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"$k$ номеров через пробел по убыванию частоты.", ['6 2\n1 1 1 2 2 3\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); hi = 4 if lv < 3 else r.choice([5, 1000, 10 ** 9]); a = [r.randint(-hi, hi) for _ in range(n)]
        return '%d %d\n%s\n' % (n, r.randint(1, len(set(a))), nums(a))

    def solve(d):
        t = ints(d); n, k = t[:2]; c = Counter(t[2:2 + n])
        return nums([x for x, _ in sorted(c.items(), key=lambda p: (-p[1], p[0]))[:k]])

    def brute(d):
        t = ints(d); n, k = t[:2]; a = t[2:2 + n]; vals = sorted(set(a)); out = []
        for _ in range(k):
            best = None
            for v in vals:
                if v in out: continue
                if best is None or a.count(v) > a.count(best): best = v
            out.append(best)
        return nums(out)


@prob('consecutive_numbers', 'Подряд идущие номера', 'training', ['Массивы', 'Структуры данных'], 36,
      r"Даны $n$ номеров юрт (возможны повторы). Найдите наибольшее количество **различных** номеров, которые образуют последовательность подряд идущих целых чисел $x, x+1, x+2, \dots$ (порядок в списке не важен).",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Длина самой длинной цепочки.", ['6\n100 4 200 1 3 2\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); base = r.randint(-10 ** 9, 10 ** 9 - n - 5) if lv > 2 else 0; hi = 8 if lv < 3 else n * 2
        return '%d\n%s\n' % (n, nums([base + r.randint(0, hi) for _ in range(n)]))

    def solve(d):
        t = ints(d); s = set(t[1:1 + t[0]]); best = 0
        for x in s:
            if x - 1 not in s:
                y = x
                while y + 1 in s: y += 1
                best = max(best, y - x + 1)
        return str(best)

    def brute(d):
        t = ints(d); a = sorted(set(t[1:1 + t[0]])); best = cur = 1
        for i in range(1, len(a)):
            cur = cur + 1 if a[i] == a[i - 1] + 1 else 1; best = max(best, cur)
        return str(best)


@prob('twin_words', 'Слова-близнецы', 'training', ['Строки'], 24,
      r"Две строки называются близнецами, если буквы одной можно взаимно однозначно заменить буквами другой (одинаковые буквы заменяются одинаковыми, разные — разными) и получить вторую строку, например `egg` и `add`, но не `foo` и `bar`. Близнецы ли данные строки?",
      r"В двух строках записаны $a$ и $b$ одинаковой длины от $1$ до $10^5$, строчные латинские буквы.",
      r"`YES` или `NO`.", ['egg\nadd\n', 'foo\nbar\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); a = word(r, n, 'abcde' if lv < 5 else 'abcdefghij')
        if r.random() < 0.6:
            perm = list('abcdefghijklmnopqrstuvwxyz'); r.shuffle(perm); b = ''.join(perm[ord(c) - 97] for c in a)
            if r.random() < 0.4 and n > 1: i = r.randrange(n); b = b[:i] + r.choice('abcdefghijklmnopqrstuvwxyz') + b[i + 1:]
        else: b = word(r, n, 'abcde' if lv < 5 else 'abcdefghij')
        return a + '\n' + b + '\n'

    def solve(d):
        a, b = d.split()[:2]; m1, m2 = {}, {}
        for x, y in zip(a, b):
            if m1.setdefault(x, y) != y or m2.setdefault(y, x) != x: return 'NO'
        return 'YES'

    def brute(d):
        a, b = d.split()[:2]
        def norm(s): return [s.index(c) for c in s]
        return 'YES' if norm(a) == norm(b) else 'NO'


@prob('min_sums', 'Минимумы отрезков', 'olympiad', ['Структуры данных', 'Массивы'], 62,
      r"Для каждого непустого отрезка подряд идущих элементов массива возьмите его минимум. Найдите сумму этих минимумов по всем отрезкам по модулю $10^9+7$.",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"Сумма по модулю $10^9+7$.", ['4\n3 1 2 4\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); hi = 5 if lv < 3 else r.choice([3, 10 ** 9]); a = [r.randint(1, hi) for _ in range(n)]
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; left = [0] * n; right = [0] * n; st = []
        for i in range(n):
            while st and a[st[-1]] > a[i]: st.pop()
            left[i] = i - (st[-1] if st else -1); st.append(i)
        st = []
        for i in range(n - 1, -1, -1):
            while st and a[st[-1]] >= a[i]: st.pop()
            right[i] = (st[-1] if st else n) - i; st.append(i)
        return str(sum(a[i] * left[i] * right[i] for i in range(n)) % MOD)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        return str(sum(min(a[i:j + 1]) for i in range(n) for j in range(i, n)) % MOD)


@prob('best_product', 'Лучшее произведение', 'olympiad', ['DP', 'Массивы'], 44,
      r"В массиве из $n$ чисел найдите непустой отрезок подряд идущих элементов с наибольшим произведением.",
      r"В первой строке $n$ ($1 \le n \le 60$). Во второй — $n$ чисел $a_i$ ($-2 \le a_i \le 2$). Ответ помещается в 64-битное целое.",
      r"Наибольшее произведение.", ['4\n2 3 -2 4\n'.replace('3', '2').replace('4', '2'), '3\n-2 0 -1\n'])
class _:
    def gen(r, lv):
        n = r.randint(1, 6) if lv < 3 else r.randint(10, 60); return '%d\n%s\n' % (n, nums([r.choice([-2, -1, 0, 1, 2, 2, -2]) for _ in range(n)]))

    def solve(d):
        t = ints(d); a = t[1:1 + t[0]]; mx = mn = best = a[0]
        for x in a[1:]:
            c = (x, mx * x, mn * x); mx, mn = max(c), min(c); best = max(best, mx)
        return str(best)

    def brute(d):
        t = ints(d); a = t[1:1 + t[0]]; best = None
        for i in range(len(a)):
            p = 1
            for j in range(i, len(a)):
                p *= a[j]; best = p if best is None or p > best else best
        return str(best)


@prob('ring_apples', 'Яблоки на кольце', 'training', ['DP'], 36,
      r"Яблони растут по кругу вокруг пруда: первая является соседкой последней. На $i$-й созрело $a_i$ яблок. Нельзя собирать с двух соседних яблонь. Какое наибольшее число яблок можно собрать?",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^4$).",
      r"Наибольшее число яблок.", ['3\n2 3 2\n', '4\n1 2 3 1\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); hi = 6 if lv < 3 else 10 ** 4; return '%d\n%s\n' % (n, nums([r.randint(0, hi) for _ in range(n)]))

    def solve(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        def line(b):
            p = q = 0
            for x in b: p, q = q, max(q, p + x)
            return q
        return str(a[0] if n == 1 else max(line(a[1:]), line(a[:-1])))

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; best = 0
        for m in range(1 << n):
            if n > 1 and (m & (m >> 1) or (m & 1 and m >> (n - 1) & 1)): continue
            best = max(best, sum(a[i] for i in range(n) if m >> i & 1))
        return str(best)


@prob('search_trees', 'Деревья поиска', 'olympiad', ['DP', 'Комбинаторика'], 52,
      r"Сколько существует различных двоичных деревьев поиска, хранящих ключи $1, 2, \dots, n$ (каждый ключ ровно один раз)? Ответ по модулю $10^9+7$.",
      r"Одно число $n$ ($1 \le n \le 1000$).",
      r"Количество деревьев по модулю $10^9+7$.", ['3\n', '1\n'])
class _:
    def gen(r, lv):
        return '%d\n' % (lv + 1 if lv < 9 else 1000) if lv < 3 else '%d\n' % [10, 50, 100, 300, 500, 700, 999][lv - 3]

    def solve(d):
        n = int(d.split()[0]); f = [1] + [0] * n
        for i in range(1, n + 1): f[i] = sum(f[j] * f[i - 1 - j] for j in range(i)) % MOD
        return str(f[n])

    def brute(d):
        n = int(d.split()[0])
        @lru_cache(None)
        def go(lo, hi):
            if lo >= hi: return 1
            return sum(go(lo, k - 1) * go(k + 1, hi) for k in range(lo, hi + 1))
        return str(go(1, n) % MOD)


@prob('felt_pyramid', 'Пирамида из кошм', 'training', ['DP'], 24,
      r"Кошмы сложены пирамидой из $n$ рядов: в $i$-м ряду $i$ кошм, у каждой есть ценность. Идя сверху вниз, с кошмы $j$ ряда $i$ можно перейти на кошму $j$ или $j+1$ следующего ряда. Какова наименьшая сумма ценностей на пути от вершины до последнего ряда?",
      r"В первой строке $n$ ($1 \le n \le 1000$). В $i$-й из следующих $n$ строк — $i$ чисел от $-10^4$ до $10^4$.",
      r"Наименьшая сумма.", ['4\n2\n3 4\n6 5 7\n4 1 8 3\n'])
class _:
    def gen(r, lv):
        n = r.randint(1, 5) if lv < 3 else size(lv, 1000); hi = 9 if lv < 3 else 10 ** 4
        return '%d\n%s' % (n, ''.join(nums([r.randint(-hi, hi) for _ in range(i)]) + '\n' for i in range(1, n + 1)))

    def solve(d):
        t = ints(d); n = t[0]; rows = []; p = 1
        for i in range(1, n + 1): rows.append(t[p:p + i]); p += i
        f = rows[-1][:]
        for i in range(n - 2, -1, -1): f = [rows[i][j] + min(f[j], f[j + 1]) for j in range(i + 1)]
        return str(f[0])

    def brute(d):
        t = ints(d); n = t[0]; rows = []; p = 1
        for i in range(1, n + 1): rows.append(t[p:p + i]); p += i
        def go(i, j): return rows[i][j] + (min(go(i + 1, j), go(i + 1, j + 1)) if i + 1 < n else 0)
        return str(go(0, 0))
