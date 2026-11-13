import re
from collections import defaultdict, Counter, OrderedDict
from functools import lru_cache
from lib import prob, size, nums, ints

MOD = 10 ** 9 + 7


def word(r, n, alpha):
    return ''.join(r.choice(alpha) for _ in range(n))


@prob('common_song', 'Общая песня', 'olympiad', ['Строки', 'DP'], 45,
      r"Два акына записали свои песни как строки из строчных латинских букв. Найдите длину наибольшей **общей подпоследовательности** (буквы берутся в том же порядке, но не обязательно подряд).",
      r"В двух строках записаны $a$ и $b$ ($1 \le |a|, |b| \le 2000$).",
      r"Длина наибольшей общей подпоследовательности.", ['abcde\nace\n', 'abc\ndef\n'], time=2)
class _:
    def gen(r, lv):
        al = 'ab' if lv < 5 else 'abcd'
        n = r.randint(1, 6) if lv < 3 else size(lv, 2000); m = r.randint(1, 6) if lv < 3 else size(lv, 2000)
        return word(r, n, al) + '\n' + word(r, m, al) + '\n'

    def solve(d):
        a, b = d.split()[:2]; prev = [0] * (len(b) + 1)
        for x in a:
            cur = [0]
            for j, y in enumerate(b):
                cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[j]))
            prev = cur
        return str(prev[-1])

    def brute(d):
        a, b = d.split()[:2]
        def sub(s, t):
            it = iter(t); return all(c in it for c in s)
        return str(max(bin(m).count('1') for m in range(1 << len(a)) if sub([a[i] for i in range(len(a)) if m >> i & 1], b)))


@prob('syllable_words', 'Слова из слогов', 'training', ['Строки', 'DP'], 34,
      r"Из слогов словаря можно составлять слова, повторяя слоги сколько угодно раз. Можно ли записанную строку $s$ разбить на подряд идущие слоги из словаря?",
      r"В первой строке $s$ ($1 \le |s| \le 2000$), во второй число $k$ слогов ($1 \le k \le 50$), далее $k$ строк со слогами (длина до 20). Все — строчные латинские буквы.",
      r"`YES` или `NO`.", ['kyrgyzstan\n3\nkyr\ngyz\nstan\n', 'abcd\n2\nab\nc\n'])
class _:
    def gen(r, lv):
        al = 'ab'; k = r.randint(1, 3 if lv < 3 else 12)
        sy = list({word(r, r.randint(1, 3 if lv < 6 else 6), al) for _ in range(k)})
        n = r.randint(1, 6) if lv < 3 else size(lv, 2000)
        if r.random() < 0.6:
            s = ''
            while len(s) < n: s += r.choice(sy)
        else:
            s = word(r, n, al)
        return '%s\n%d\n%s\n' % (s, len(sy), '\n'.join(sy))

    def solve(d):
        t = d.split(); s = t[0]; w = t[2:2 + int(t[1])]; f = [True] + [False] * len(s)
        for i in range(1, len(s) + 1):
            f[i] = any(i >= len(x) and f[i - len(x)] and s[i - len(x):i] == x for x in w)
        return 'YES' if f[-1] else 'NO'

    def brute(d):
        t = d.split(); s = t[0]; w = t[2:2 + int(t[1])]
        return 'YES' if re.fullmatch('(' + '|'.join(w) + ')*', s) else 'NO'


@prob('decode_letter', 'Расшифровка письма', 'training', ['DP', 'Строки'], 38,
      r"Письмо зашифровано цифрами: букве с номером от 1 до 26 соответствует число без ведущего нуля (`1` = А, ..., `26` = Я). Сколькими способами можно разбить строку цифр на такие числа? Выведите ответ по модулю $10^9+7$.",
      r"Одна строка из цифр длиной от $1$ до $10^5$.",
      r"Число способов по модулю $10^9+7$ (если способов нет, выведите $0$).", ['226\n', '06\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5)
        return word(r, n, '0112233456789' if lv % 2 else '12') + '\n'

    def solve(d):
        s = d.split()[0]; a, b = 1, 0
        for i, c in enumerate(s):
            cur = 0
            if c != '0': cur += a
            if i and s[i - 1] != '0' and int(s[i - 1:i + 1]) <= 26: cur += b
            a, b = cur % MOD, a
        return str(a)

    def brute(d):
        s = d.split()[0]
        @lru_cache(None)
        def f(i):
            if i == len(s): return 1
            if s[i] == '0': return 0
            res = f(i + 1)
            if i + 1 < len(s) and int(s[i:i + 2]) <= 26: res += f(i + 2)
            return res
        import sys; sys.setrecursionlimit(10000)
        return str(f(0) % MOD)


def grid_gen(r, lv, big, p):
    h = r.randint(1, 4) if lv < 3 else size(lv, big); w = r.randint(1, 4) if lv < 3 else size(lv, big)
    g = [['#' if r.random() < p else '.' for _ in range(w)] for _ in range(h)]
    g[0][0] = g[h - 1][w - 1] = '.'
    return h, w, g


@prob('rock_paths', 'Тропы между скал', 'training', ['DP', 'Комбинаторика'], 36,
      r"Турист идёт по карте $h \times w$ из левого верхнего угла в правый нижний, делая шаги только **вправо** или **вниз**. Клетки `#` — скалы, туда ступать нельзя. Сколько существует разных маршрутов? Ответ по модулю $10^9+7$.",
      r"В первой строке $h$ и $w$ ($1 \le h, w \le 1000$). Далее $h$ строк из `.` и `#`. Начальная и конечная клетки свободны.",
      r"Число маршрутов по модулю $10^9+7$.", ['3 3\n...\n.#.\n...\n'])
class _:
    def gen(r, lv):
        h, w, g = grid_gen(r, lv, 600, 0.1 if lv > 4 else 0.25)
        return '%d %d\n%s\n' % (h, w, '\n'.join(map(''.join, g)))

    def solve(d):
        t = d.split(); h, w = int(t[0]), int(t[1]); g = t[2:2 + h]; f = [0] * w; f[0] = 1
        for i in range(h):
            for j in range(w):
                if g[i][j] == '#': f[j] = 0
                elif j: f[j] = (f[j] + f[j - 1]) % MOD
        return str(f[-1] % MOD)

    def brute(d):
        t = d.split(); h, w = int(t[0]), int(t[1]); g = t[2:2 + h]
        @lru_cache(None)
        def go(i, j):
            if g[i][j] == '#': return 0
            if i == h - 1 and j == w - 1: return 1
            return (go(i + 1, j) if i + 1 < h else 0) + (go(i, j + 1) if j + 1 < w else 0)
        return str(go(0, 0) % MOD)


@prob('light_path', 'Лёгкий путь с перевала', 'training', ['DP'], 32,
      r"На карте $h \times w$ в каждой клетке записана тяжесть подъёма $c_{ij}$. Из левого верхнего угла в правый нижний можно идти только вправо или вниз. Найдите наименьшую сумму тяжестей на пути (обе угловые клетки считаются).",
      r"В первой строке $h$ и $w$ ($1 \le h, w \le 1000$). Далее $h$ строк по $w$ чисел $c_{ij}$ ($0 \le c_{ij} \le 1000$).",
      r"Наименьшая сумма.", ['3 3\n1 3 1\n1 5 1\n4 2 1\n'])
class _:
    def gen(r, lv):
        h = r.randint(1, 4) if lv < 3 else size(lv, 700); w = r.randint(1, 4) if lv < 3 else size(lv, 700)
        hi = 9 if lv < 3 else 1000
        return '%d %d\n%s' % (h, w, ''.join(nums([r.randint(0, hi) for _ in range(w)]) + '\n' for _ in range(h)))

    def solve(d):
        t = ints(d); h, w = t[0], t[1]; c = t[2:]; f = [10 ** 18] * w; f[0] = 0
        for i in range(h):
            for j in range(w):
                best = f[j] if i else (0 if j == 0 else 10 ** 18)
                if j: best = min(best, f[j - 1])
                f[j] = best + c[i * w + j]
        return str(f[-1])

    def brute(d):
        t = ints(d); h, w = t[0], t[1]; c = t[2:]
        @lru_cache(None)
        def go(i, j):
            if i == h - 1 and j == w - 1: return c[i * w + j]
            opts = []
            if i + 1 < h: opts.append(go(i + 1, j))
            if j + 1 < w: opts.append(go(i, j + 1))
            return c[i * w + j] + min(opts)
        return str(go(0, 0))


@prob('equal_inheritance', 'Делёж наследства', 'training', ['DP'], 40,
      r"Три брата делят наследство: $n$ предметов стоимостью $a_i$. Можно ли разделить предметы на две группы с одинаковой суммарной стоимостью (каждый предмет в одной группе)?",
      r"В первой строке $n$ ($1 \le n \le 200$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 100$).",
      r"`YES` или `NO`.", ['4\n1 5 11 5\n', '4\n1 2 3 5\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200); hi = 6 if lv < 3 else 100
        a = [r.randint(1, hi) for _ in range(n)]
        if r.random() < 0.5 and n > 1:
            s = sum(a[:-1]); a[-1] = max(1, s // 2) if s % 2 == 0 else a[-1]
            a[-1] = sum(a[:-1]) if r.random() < 0.5 else a[-1]
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        t = ints(d); a = t[1:1 + t[0]]; s = sum(a)
        if s % 2: return 'NO'
        bits = 1
        for x in a: bits |= bits << x
        return 'YES' if bits >> (s // 2) & 1 else 'NO'

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]; s = sum(a)
        return 'YES' if any(2 * sum(a[i] for i in range(n) if m >> i & 1) == s for m in range(1 << n)) else 'NO'


@prob('coin_ways', 'Размен без порядка', 'olympiad', ['DP', 'Комбинаторика'], 42,
      r"Есть монеты $k$ различных номиналов, каждого номинала сколько угодно. Сколькими способами можно набрать ровно $S$ сомов, если способы, отличающиеся только порядком монет, считаются одинаковыми? Ответ по модулю $10^9+7$.",
      r"В первой строке $k$ и $S$ ($1 \le k \le 50$, $0 \le S \le 10^5$). Во второй — $k$ различных номиналов ($1 \le c_i \le 10^5$).",
      r"Число способов по модулю $10^9+7$.", ['3 5\n1 2 5\n', '1 3\n2\n'], time=2)
class _:
    def gen(r, lv):
        k = r.randint(1, 3 if lv < 3 else 20); S = r.randint(0, 15) if lv < 3 else size(lv, 10 ** 5)
        c = r.sample(range(1, 8 if lv < 3 else 500), min(k, 7 if lv < 3 else 499))
        return '%d %d\n%s\n' % (len(c), S, nums(c))

    def solve(d):
        t = ints(d); k, s = t[0], t[1]; f = [1] + [0] * s
        for c in t[2:2 + k]:
            for v in range(c, s + 1): f[v] = (f[v] + f[v - c]) % MOD
        return str(f[s])

    def brute(d):
        t = ints(d); k, s = t[0], t[1]; c = t[2:2 + k]
        def go(i, rest):
            if rest == 0: return 1
            if i == k: return 0
            return sum(go(i + 1, rest - x * c[i]) for x in range(rest // c[i] + 1))
        return str(go(0, s) % MOD)


@prob('square_carpets', 'Квадратные ковры', 'training', ['DP', 'Математика'], 38,
      r"Ковёр площади $n$ нужно сшить из квадратных лоскутов со стороной в целое число метров. Какое наименьшее число лоскутов нужно, чтобы их суммарная площадь была ровно $n$?",
      r"Одно число $n$ ($1 \le n \le 10^4$).",
      r"Наименьшее число лоскутов.", ['12\n', '13\n'])
class _:
    def gen(r, lv):
        return '%d\n' % (r.randint(1, 30) if lv < 3 else [10 ** 3, 5000, 7000, 8191, 9000, 9999, 10 ** 4][min(6, lv - 3)] - r.randint(0, 7))

    def solve(d):
        n = int(d.split()[0]); f = [0] + [10 ** 9] * n
        for v in range(1, n + 1):
            k = 1
            while k * k <= v:
                f[v] = min(f[v], f[v - k * k] + 1); k += 1
        return str(f[n])

    def brute(d):
        n = int(d.split()[0]); seen = {0}; fr = [0]; steps = 0
        while n not in seen:
            steps += 1; nxt = set()
            for v in fr:
                k = 1
                while v + k * k <= n:
                    nxt.add(v + k * k); k += 1
            fr = list(nxt - seen); seen |= nxt
        return str(steps)


@prob('thread_patterns', 'Узоры из нитей', 'olympiad', ['DP', 'Строки'], 50,
      r"Сколько раз строка $t$ встречается в строке $s$ как **подпоследовательность** (позиции букв $s$ идут в порядке возрастания, но не обязательно подряд; разные наборы позиций считаются разными)? Ответ по модулю $10^9+7$.",
      r"В первой строке $s$, во второй $t$ ($1 \le |s|, |t| \le 2000$), строчные латинские буквы.",
      r"Число вхождений по модулю $10^9+7$.", ['rabbbit\nrabbit\n', 'babgbag\nbag\n'], time=2)
class _:
    def gen(r, lv):
        n = r.randint(1, 8) if lv < 3 else size(lv, 2000); m = r.randint(1, 4) if lv < 3 else max(1, size(lv, 1000))
        al = 'ab' if lv % 2 == 0 else 'abc'
        return word(r, n, al) + '\n' + word(r, m, al) + '\n'

    def solve(d):
        s, t = d.split()[:2]; f = [1] + [0] * len(t)
        for c in s:
            for j in range(len(t), 0, -1):
                if t[j - 1] == c: f[j] = (f[j] + f[j - 1]) % MOD
        return str(f[-1])

    def brute(d):
        s, t = d.split()[:2]
        @lru_cache(None)
        def go(i, j):
            if j == len(t): return 1
            if i == len(s): return 0
            return go(i + 1, j) + (go(i + 1, j + 1) if s[i] == t[j] else 0)
        return str(go(0, 0) % MOD)


@prob('count_palins', 'Счастливые палиндромы', 'training', ['Строки'], 34,
      r"Сколько в строке $s$ подстрок-палиндромов? Подстроки с разными позициями считаются разными, даже если они совпадают как строки.",
      r"Одна строка $s$ из строчных латинских букв, $1 \le |s| \le 3000$.",
      r"Количество палиндромических подстрок.", ['abc\n', 'aaa\n'], time=2)
class _:
    def gen(r, lv):
        n = size(lv, 3000)
        return ('a' * n if lv > 3 and lv % 4 == 0 else word(r, n, 'ab' if lv % 2 else 'abc')) + '\n'

    def solve(d):
        s = d.split()[0]; n = len(s); cnt = 0
        for c in range(n):
            for l, r_ in ((c, c), (c, c + 1)):
                while l >= 0 and r_ < n and s[l] == s[r_]:
                    cnt += 1; l -= 1; r_ += 1
        return str(cnt)

    def brute(d):
        s = d.split()[0]
        return str(sum(1 for i in range(len(s)) for j in range(i + 1, len(s) + 1) if s[i:j] == s[i:j][::-1]))


@prob('replace_pattern', 'Выровнять узор', 'olympiad', ['Строки', 'Двоичный поиск'], 46,
      r"В строке $s$ можно заменить не более $k$ символов на любые другие. Какой наибольшей длины подстроку, состоящую из одинаковых букв, можно получить?",
      r"В первой строке $s$ ($1 \le |s| \le 10^5$, заглавные латинские буквы), во второй число $k$ ($0 \le k \le |s|$).",
      r"Наибольшая длина.", ['ABAB\n2\n', 'AABABBA\n1\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); s = word(r, n, 'AB' if lv < 5 else 'ABC')
        return s + '\n%d\n' % r.randint(0, min(n, 3 if lv < 3 else n // 3))

    def solve(d):
        s, k = d.split()[0], int(d.split()[1]); cnt = Counter(); j = best = mx = 0
        for i, c in enumerate(s):
            cnt[c] += 1; mx = max(mx, cnt[c])
            if i - j + 1 - mx > k:
                cnt[s[j]] -= 1; j += 1
            best = max(best, i - j + 1)
        return str(best)

    def brute(d):
        s, k = d.split()[0], int(d.split()[1]); n = len(s); best = 0
        for i in range(n):
            for j in range(i, n):
                sub = s[i:j + 1]
                if len(sub) - max(sub.count(c) for c in set(sub)) <= k: best = max(best, len(sub))
        return str(best)


@prob('name_anagrams', 'Анаграммы имён', 'training', ['Строки', 'Сортировка'], 24,
      r"Два слова называются родственными, если из букв одного можно составить другое. Даны $n$ имён. На сколько групп они разбиваются, если в одну группу входят все родственные имена?",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Далее $n$ строк — имена из строчных латинских букв (длина до 20).",
      r"Количество групп.", ['5\nakyn\nkyna\nala\nlaa\nsoz\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5)
        names = [word(r, r.randint(1, 4 if lv < 6 else 8), 'abc') for _ in range(n)]
        return '%d\n%s\n' % (n, '\n'.join(names))

    def solve(d):
        t = d.split(); return str(len({''.join(sorted(w)) for w in t[1:1 + int(t[0])]}))

    def brute(d):
        t = d.split(); ws = t[1:1 + int(t[0])]; p = list(range(len(ws)))
        def f(x):
            while p[x] != x: x = p[x]
            return x
        for i in range(len(ws)):
            for j in range(i):
                if Counter(ws[i]) == Counter(ws[j]): p[f(i)] = f(j)
        return str(len({f(i) for i in range(len(ws))}))


@prob('lone_letter', 'Единственная буква', 'training', ['Строки'], 12,
      r"Найдите в строке первый (самый левый) символ, который встречается в ней ровно один раз, и выведите его номер (с 1). Если такого символа нет, выведите $-1$.",
      r"Одна строка из строчных латинских букв, $1 \le |s| \le 10^5$.",
      r"Номер символа или $-1$.", ['kyrgyz\n', 'aabb\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5)
        h = (n + 1) // 2; s = word(r, h, 'abcdefghij')
        s = s + s[: n - h] if lv % 3 == 0 and lv > 3 else word(r, n, 'abcdefghijklmnopqrstuvwxyz'[:3 if lv < 3 else 26])
        return s + '\n'

    def solve(d):
        s = d.split()[0]; c = Counter(s)
        return str(next((i + 1 for i, ch in enumerate(s) if c[ch] == 1), -1))

    def brute(d):
        s = d.split()[0]
        return str(next((i + 1 for i in range(len(s)) if s.count(s[i]) == 1), -1))


@prob('common_start', 'Общее начало', 'training', ['Строки'], 14,
      r"Найдите самое длинное общее начало (префикс) всех $n$ названий. Если общего начала нет, выведите пустую строку.",
      r"В первой строке $n$ ($1 \le n \le 1000$). Далее $n$ непустых строк из строчных латинских букв, суммарная длина не больше $10^5$.",
      r"Общий префикс (возможно, пустая строка).", ['3\nkyrgyz\nkyrgyzstan\nkyr\n', '2\nala\ntoo\n'])
class _:
    def gen(r, lv):
        n = r.randint(1, 3) if lv < 3 else size(lv, 1000); base = word(r, r.randint(0, 6 if lv < 3 else 40), 'ab')
        L = max(1, 100 // n if lv > 3 else 6)
        return '%d\n%s\n' % (n, '\n'.join(base + word(r, r.randint(1 if not base else 0, L), 'ab') or 'a' for _ in range(n)))

    def solve(d):
        w = d.split()[1:]; w = w[:int(d.split()[0])]; p = w[0]
        for x in w[1:]:
            while not x.startswith(p): p = p[:-1]
        return p

    def brute(d):
        w = d.split()[1:]; w = w[:int(d.split()[0])]; res = ''
        for i in range(1, min(map(len, w)) + 1):
            if len({x[:i] for x in w}) == 1: res = w[0][:i]
        return res


@prob('medal_numbers', 'Римские цифры на медали', 'training', ['Строки', 'Реализация'], 20,
      r"На медалях годы выбиты римскими цифрами (`I`=1, `V`=5, `X`=10, `L`=50, `C`=100, `D`=500, `M`=1000). Если меньшая цифра стоит перед большей, она вычитается (`IV`=4, `IX`=9, `XL`=40, `XC`=90, `CD`=400, `CM`=900). Переведите число в десятичную запись.",
      r"Одна строка — корректное римское число от $1$ до $3999$.",
      r"Число в десятичной записи.", ['MCMXCIV\n', 'III\n'])
class _:
    def gen(r, lv):
        n = r.randint(1, 20) if lv < 3 else r.randint(1, 3999)
        out = ''
        for v, s in ((1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')):
            while n >= v: out += s; n -= v
        return out + '\n'

    def solve(d):
        v = dict(I=1, V=5, X=10, L=50, C=100, D=500, M=1000); s = d.split()[0]
        return str(sum(-v[c] if i + 1 < len(s) and v[c] < v[s[i + 1]] else v[c] for i, c in enumerate(s)))

    def brute(d):
        s = d.split()[0]; tot = 0
        for a, b in (('CM', 900), ('CD', 400), ('XC', 90), ('XL', 40), ('IX', 9), ('IV', 4)):
            tot += s.count(a) * b; s = s.replace(a, '')
        return str(tot + sum({'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}[c] for c in s))


@prob('binary_sum', 'Двоичные подсчёты', 'training', ['Строки', 'Математика'], 22,
      r"Два длинных числа записаны в двоичной системе. Выведите их сумму тоже в двоичной системе без ведущих нулей (число $0$ записывается как `0`).",
      r"В двух строках записаны числа из символов `0` и `1`, длина каждого от $1$ до $10^5$, ведущие нули допускаются.",
      r"Сумма в двоичной записи.", ['11\n1\n', '0\n000\n'])
class _:
    def gen(r, lv):
        a = word(r, size(lv, 10 ** 5), '01'); b = word(r, size(lv, 10 ** 5), '1' if lv > 4 and lv % 3 == 0 else '01')
        return a + '\n' + b + '\n'

    def solve(d):
        a, b = d.split()[:2]; n = max(len(a), len(b)); a = a.zfill(n); b = b.zfill(n); c = 0; res = []
        for i in range(n - 1, -1, -1):
            s = int(a[i]) + int(b[i]) + c; res.append(str(s & 1)); c = s >> 1
        if c: res.append('1')
        r = ''.join(reversed(res)).lstrip('0')
        return r or '0'

    def brute(d):
        a, b = d.split()[:2]; return bin(int(a, 2) + int(b, 2))[2:]


@prob('echo_count', 'Эхо в горах', 'olympiad', ['Строки'], 42,
      r"В тексте $s$ нужно найти, сколько раз встречается образец $p$ (вхождения могут пересекаться).",
      r"В первой строке $s$, во второй $p$ ($1 \le |p|, |s| \le 10^5$), строчные латинские буквы.",
      r"Количество вхождений.", ['aaaa\naa\n', 'abcab\nab\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); al = 'ab' if lv % 2 else 'a'
        s = word(r, n, al if lv > 2 else 'ab'); m = r.randint(1, min(n, 3 if lv < 6 else 20))
        p = s[:m] if r.random() < 0.7 else word(r, m, al)
        return s + '\n' + p + '\n'

    def solve(d):
        s, p = d.split()[:2]; z = p + '#' + s; n = len(z); pi = [0] * n; cnt = 0
        for i in range(1, n):
            k = pi[i - 1]
            while k and z[i] != z[k]: k = pi[k - 1]
            if z[i] == z[k]: k += 1
            pi[i] = k
            if k == len(p): cnt += 1
        return str(cnt)

    def brute(d):
        s, p = d.split()[:2]
        return str(sum(1 for i in range(len(s) - len(p) + 1) if s[i:i + len(p)] == p))


@prob('short_record', 'Короткая запись', 'olympiad', ['Строки', 'Двоичный поиск'], 52,
      r"Найдите кратчайшую подстроку строки $s$, в которой каждая буква строки $t$ встречается не меньше раз, чем в $t$ (с учётом повторов). Выведите её длину или $-1$, если такой подстроки нет.",
      r"В первой строке $s$ ($1 \le |s| \le 10^5$), во второй $t$ ($1 \le |t| \le 10^5$), строчные латинские буквы.",
      r"Длина кратчайшей подстроки или $-1$.", ['ADOBECODEBANC\nABC\n'.lower(), 'a\naa\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); s = word(r, n, 'abc' if lv < 5 else 'abcdef'); m = r.randint(1, min(n, 3 if lv < 3 else 8))
        t = ''.join(r.sample(s, m)) if r.random() < 0.8 else word(r, m, 'abcz')
        return s + '\n' + t + '\n'

    def solve(d):
        s, t = d.split()[:2]; need = Counter(t); miss = len(t); best = 10 ** 9; j = 0
        for i, c in enumerate(s):
            if need[c] > 0: miss -= 1
            need[c] -= 1
            while miss == 0:
                best = min(best, i - j + 1); need[s[j]] += 1
                if need[s[j]] > 0: miss += 1
                j += 1
        return str(best if best < 10 ** 9 else -1)

    def brute(d):
        s, t = d.split()[:2]; ct = Counter(t); best = -1
        for i in range(len(s)):
            for j in range(i + len(t), len(s) + 1):
                if not (ct - Counter(s[i:j])):
                    if best == -1 or j - i < best: best = j - i
                    break
        return str(best)


@prob('bazaar_cache', 'Кэш на базаре', 'olympiad', ['Структуры данных'], 46,
      r"Продавец держит на прилавке не более $c$ товаров. Каждый запрос — номер товара. Если товар на прилавке, он «освежается» (становится самым недавним). Иначе его кладут на прилавок, а если места нет, убирают товар, к которому дольше всего не обращались. Сколько запросов найдёт товар уже на прилавке?",
      r"В первой строке $c$ и $q$ ($1 \le c \le 10^5$, $1 \le q \le 10^5$). Во второй — $q$ номеров $x_i$ ($1 \le x_i \le 10^9$).",
      r"Количество найденных запросов.", ['2 6\n1 2 1 3 2 1\n'])
class _:
    def gen(r, lv):
        q = size(lv, 10 ** 5); c = r.randint(1, 3) if lv < 3 else r.randint(1, 500); top = 4 if lv < 3 else r.choice([10, 600, 5000])
        return '%d %d\n%s\n' % (c, q, nums([r.randint(1, top) for _ in range(q)]))

    def solve(d):
        t = ints(d); c, q = t[0], t[1]; od = OrderedDict(); hit = 0
        for x in t[2:2 + q]:
            if x in od: hit += 1; od.move_to_end(x)
            else:
                od[x] = 1
                if len(od) > c: od.popitem(last=False)
        return str(hit)

    def brute(d):
        t = ints(d); c, q = t[0], t[1]; lst = []; hit = 0
        for x in t[2:2 + q]:
            if x in lst: hit += 1; lst.remove(x); lst.append(x)
            else:
                lst.append(x)
                if len(lst) > c: lst.pop(0)
        return str(hit)


@prob('long_ornament', 'Длинный правильный орнамент', 'olympiad', ['Строки', 'Структуры данных'], 50,
      r"Дана строка из скобок `(` и `)`. Найдите длину самой длинной **подстроки**, которая является правильной скобочной последовательностью.",
      r"Одна непустая строка из `(` и `)` длиной до $10^5$.",
      r"Длина самой длинной правильной подстроки.", ['(()\n', ')()())\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); p = r.choice([0.5, 0.6, 0.4])
        return ''.join('(' if r.random() < p else ')' for _ in range(n)) + '\n'

    def solve(d):
        s = d.split()[0]; st = [-1]; best = 0
        for i, c in enumerate(s):
            if c == '(': st.append(i)
            else:
                st.pop()
                if not st: st.append(i)
                else: best = max(best, i - st[-1])
        return str(best)

    def brute(d):
        s = d.split()[0]; best = 0
        for i in range(len(s)):
            bal = 0
            for j in range(i, len(s)):
                bal += 1 if s[j] == '(' else -1
                if bal < 0: break
                if bal == 0: best = max(best, j - i + 1)
        return str(best)
