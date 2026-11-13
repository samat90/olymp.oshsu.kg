from reg import task, LIN, MID, QUAD, SMALLQ

BIG = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]


@task('flip_alternate', 'Чередование с поворотом',
"""Двоичную строку можно как угодно циклически сдвигать (это бесплатно) и менять отдельные символы (`0` на `1` или наоборот), каждая замена стоит один ход. Какое наименьшее число замен нужно, чтобы после этого строка стала чередующейся (никакие два соседних символа не равны), если сдвиги можно делать в любое время и сколько угодно?

## Вход

Одна строка из `0` и `1`, длина от 1 до 200000.

## Выход

Наименьшее число замен.""",
["111000", "010"], sizes=BIG, diff=45)
def _():
    def gen(n, rnd, k):
        p = rnd.choice([0.5, 0.2, 0.8])
        return ''.join('1' if rnd.random() < p else '0' for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        n = len(s)
        d = s + s
        diff = 0
        best = n
        for i in range(2 * n):
            if (ord(d[i]) - 48) != i % 2:
                diff += 1
            if i >= n and (ord(d[i - n]) - 48) != (i - n) % 2:
                diff -= 1
            if i >= n - 1:
                best = min(best, diff, n - diff)
        return str(best)

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        best = n
        for r in range(n):
            t = s[r:] + s[:r]
            a = sum(1 for i in range(n) if int(t[i]) != i % 2)
            best = min(best, a, n - a)
        return str(best)
    return gen, sol, brute


@task('flip_monotone', 'Нули, затем единицы',
"""Двоичную строку нужно превратить в строку вида «сначала нули, потом единицы» (любая из частей может быть пустой). За один ход меняют один символ. Какое наименьшее число ходов нужно?

## Вход

Одна строка из `0` и `1`, длина от 1 до 200000.

## Выход

Наименьшее число ходов.""",
["00110", "010110"], sizes=BIG, diff=30)
def _():
    def gen(n, rnd, k):
        p = rnd.choice([0.5, 0.2, 0.8])
        return ''.join('1' if rnd.random() < p else '0' for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        ones = 0
        res = 0
        for c in s:
            if c == '1':
                ones += 1
            else:
                res = min(res + 1, ones)
        return str(res)

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        return str(min(s[:i].count('1') + s[i:].count('0') for i in range(n + 1)))
    return gen, sol, brute


@task('equal_groups', 'Равные группы нулей и единиц',
"""Сколько в двоичной строке подстрок, которые состоят из k нулей подряд и затем k единиц подряд, либо из k единиц подряд и затем k нулей подряд (k ≥ 1)? Подстроки с разными позициями считаются разными.

## Вход

Одна строка из `0` и `1`, длина от 1 до 200000.

## Выход

Количество подстрок.""",
["00110011", "10101"], sizes=BIG, diff=25)
def _():
    def gen(n, rnd, k):
        s = []
        while len(s) < n:
            s += [rnd.choice('01')] * rnd.randint(1, 4 if k < 8 else 1000)
        return ''.join(s[:n]) + '\n'

    def sol(inp):
        s = inp.split()[0]
        runs = []
        i = 0
        while i < len(s):
            j = i
            while j < len(s) and s[j] == s[i]:
                j += 1
            runs.append(j - i)
            i = j
        return str(sum(min(runs[i], runs[i + 1]) for i in range(len(runs) - 1)))

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        cnt = 0
        for i in range(n):
            for j in range(i + 2, n + 1, 2):
                t = s[i:j]
                h = len(t) // 2
                if t == '0' * h + '1' * h or t == '1' * h + '0' * h:
                    cnt += 1
        return str(cnt)
    return gen, sol, brute


@task('split_score', 'Разрез с очками',
"""Двоичную строку разрезают на две непустые части. Очки разреза: число нулей в левой части плюс число единиц в правой. Найдите наибольшее число очков.

## Вход

Одна строка из `0` и `1`, длина от 2 до 200000.

## Выход

Наибольшее число очков.""",
["011101", "00"], sizes=[2, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000], diff=10)
def _():
    def gen(n, rnd, k):
        n = max(2, n)
        return ''.join(rnd.choice('01') for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        ones = s.count('1')
        zeros = 0
        best = -1
        for i in range(len(s) - 1):
            if s[i] == '0':
                zeros += 1
            else:
                ones -= 1
            best = max(best, zeros + ones)
        return str(best)

    def brute(inp):
        s = inp.split()[0]
        return str(max(s[:i].count('0') + s[i:].count('1') for i in range(1, len(s))))
    return gen, sol, brute


@task('partition_labels', 'Разбить без общих букв',
"""Слово нужно разрезать на как можно большее число частей так, чтобы никакая буква не встречалась в двух разных частях. Выведите длины частей.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Длины частей слева направо через пробел.""",
["ababcbacadefegdehijhklij", "aaa"], sizes=BIG, diff=30)
def _():
    def gen(n, rnd, k):
        s = []
        while len(s) < n:
            m = rnd.randint(1, 8 if k < 7 else 3000)
            a0 = rnd.randint(0, 20)
            al = 'abcdefghijklmnopqrstuvwxyz'[a0:a0 + rnd.randint(1, 5)]
            s += [rnd.choice(al) for _ in range(m)]
        return ''.join(s[:n]) + '\n'

    def sol(inp):
        s = inp.split()[0]
        last = {c: i for i, c in enumerate(s)}
        res = []
        st = end = 0
        for i, c in enumerate(s):
            end = max(end, last[c])
            if i == end:
                res.append(i - st + 1)
                st = i + 1
        return ' '.join(map(str, res))

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        cuts = [0] + [i for i in range(1, n) if not (set(s[:i]) & set(s[i:]))] + [n]
        return ' '.join(str(cuts[i + 1] - cuts[i]) for i in range(len(cuts) - 1))
    return gen, sol, brute


@task('remove_digits', 'Стереть цифры',
"""Из записи числа нужно стереть ровно k цифр (оставшиеся склеиваются, порядок сохраняется), чтобы получилось наименьшее возможное число. Ведущие нули результата отбрасываются; если ничего не осталось, результат равен 0.

## Вход

В первой строке число k. Во второй строке запись числа из цифр, длина n от 1 до 200000, 0 ≤ k ≤ n.

## Выход

Наименьшее число без ведущих нулей.""",
["3\n1432219", "2\n10200"], sizes=BIG, diff=40)
def _():
    def gen(n, rnd, k):
        s = ''.join(rnd.choice('0123456789' if k > 3 else '0123') for _ in range(n))
        kk = rnd.randint(0, n)
        if k > 4 and rnd.random() < 0.5:
            kk = rnd.randint(0, n // 2)
        return str(kk) + '\n' + s + '\n'

    def sol(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        st = []
        for c in s:
            while k and st and st[-1] > c:
                st.pop()
                k -= 1
            st.append(c)
        if k:
            st = st[:-k]
        return ''.join(st).lstrip('0') or '0'

    def brute(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        n = len(s)
        from itertools import combinations
        best = None
        for idx in combinations(range(n), n - k):
            t = ''.join(s[i] for i in idx).lstrip('0') or '0'
            key = (len(t), t)
            if best is None or key < best:
                best = key
        return best[1]
    return gen, sol, brute


@task('largest_concat', 'Самое большое число из кусков',
"""Даны числа, записанные строками цифр. Выпишите их подряд в некотором порядке так, чтобы получившаяся запись была числом, наибольшим из возможных.

## Вход

В первой строке число n (1 ≤ n ≤ 50000). Во второй строке n чисел через пробел (каждое от 0 до 10^9, без ведущих нулей).

## Выход

Наибольшее возможное число (если все числа нули, выведите `0`).""",
["3\n3 30 34", "2\n10 2"], sizes=[3, 8, 15, 100, 1000, 5000, 10000, 20000, 50000, 50000], diff=40)
def _():
    def gen(n, rnd, k):
        if k == 0:
            n = min(n, 6)
        xs = []
        for _ in range(n):
            r = rnd.random()
            if r < 0.3:
                xs.append(rnd.randint(0, 99))
            elif r < 0.6:
                xs.append(rnd.choice([3, 30, 34, 5, 50, 505, 9, 90, 909, 1, 10, 100]))
            else:
                xs.append(rnd.randint(0, 10 ** 9))
        return str(n) + '\n' + ' '.join(map(str, xs)) + '\n'

    def sol(inp):
        from functools import cmp_to_key
        a = inp.split()
        n = int(a[0])
        w = a[1:n + 1]
        w.sort(key=cmp_to_key(lambda x, y: -1 if x + y > y + x else (1 if x + y < y + x else 0)))
        r = ''.join(w)
        return '0' if r[0] == '0' else r

    def brute(inp):
        from itertools import permutations
        a = inp.split()
        n = int(a[0])
        w = a[1:n + 1]
        best = max(permutations(w), key=lambda p: (len(''.join(p).lstrip('0')), ''.join(p)))
        r = ''.join(best)
        return '0' if r[0] == '0' else r
    return gen, sol, brute


@task('word_break_ways', 'Разбить на слова',
"""Дан словарь и строка без пробелов. Сколькими способами строку можно записать как последовательность слов словаря (слова можно использовать повторно)?

## Вход

В первой строке строка s из строчных латинских букв, длина от 1 до 2000. Во второй строке число слов m (1 ≤ m ≤ 1000). Затем m различных слов из строчных латинских букв длиной от 1 до 30 (каждое на своей строке).

## Выход

Количество способов по модулю 1000000007.""",
["abab\n3\na\nb\nab", "abc\n1\nd"], sizes=[3, 8, 15, 50, 100, 300, 600, 1000, 1500, 2000], diff=40)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 7 else 'abc'
        s = ''.join(rnd.choice(al) for _ in range(n))
        m = rnd.randint(1, 4 if k == 0 else 300)
        ws = set()
        for _ in range(m):
            ws.add(''.join(rnd.choice(al) for _ in range(rnd.randint(1, 3 if k < 7 else 6))))
        if k > 5:
            ws.add('a')
            ws.add('b')
        ws = sorted(ws)
        return s + '\n' + str(len(ws)) + '\n' + '\n'.join(ws) + '\n'

    def sol(inp):
        a = inp.split()
        s = a[0]
        m = int(a[1])
        ws = set(a[2:2 + m])
        lens = sorted(set(len(w) for w in ws))
        M = 10 ** 9 + 7
        n = len(s)
        dp = [0] * (n + 1)
        dp[0] = 1
        for i in range(1, n + 1):
            t = 0
            for L in lens:
                if L > i:
                    break
                if s[i - L:i] in ws:
                    t += dp[i - L]
            dp[i] = t % M
        return str(dp[n])

    def brute(inp):
        a = inp.split()
        s = a[0]
        m = int(a[1])
        ws = a[2:2 + m]

        def go(i):
            if i == len(s):
                return 1
            return sum(go(i + len(w)) for w in ws if s.startswith(w, i))
        return str(go(0) % (10 ** 9 + 7))
    return gen, sol, brute


@task('interleave', 'Перемешать два слова',
"""Слово c получено перемешиванием слов a и b, если буквы c можно разделить на две группы так, что одна группа, прочитанная по порядку, даёт a, а другая даёт b. Проверьте, получено ли c перемешиванием a и b.

## Вход

Три строки a, b и c из строчных латинских букв. Длины a и b от 1 до 500, длина c от 1 до 1000.

## Выход

`YES` или `NO`.""",
["ab\ncd\nacbd", "ab\nab\naabb"], sizes=[2, 4, 7, 20, 50, 100, 200, 300, 400, 500], diff=40)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 7 else 'abc'
        a = ''.join(rnd.choice(al) for _ in range(n))
        b = ''.join(rnd.choice(al) for _ in range(max(1, n + rnd.randint(-1, 1))))
        i = j = 0
        c = []
        while i < len(a) or j < len(b):
            if j == len(b) or (i < len(a) and rnd.random() < 0.5):
                c.append(a[i])
                i += 1
            else:
                c.append(b[j])
                j += 1
        if rnd.random() < 0.4:
            c[rnd.randrange(len(c))] = rnd.choice(al)
        elif rnd.random() < 0.3:
            rnd.shuffle(c)
        return a + '\n' + b + '\n' + ''.join(c) + '\n'

    def sol(inp):
        a, b, c = inp.split()[:3]
        n, m = len(a), len(b)
        if n + m != len(c):
            return 'NO'
        dp = [False] * (m + 1)
        for i in range(n + 1):
            for j in range(m + 1):
                if i == 0 and j == 0:
                    dp[j] = True
                    continue
                v = False
                if i and dp[j] and a[i - 1] == c[i + j - 1]:
                    v = True
                if j and dp[j - 1] and b[j - 1] == c[i + j - 1]:
                    v = True
                dp[j] = v
        return 'YES' if dp[m] else 'NO'

    def brute(inp):
        a, b, c = inp.split()[:3]
        if len(a) + len(b) != len(c):
            return 'NO'

        def go(i, j):
            if i + j == len(c):
                return True
            if i < len(a) and a[i] == c[i + j] and go(i + 1, j):
                return True
            if j < len(b) and b[j] == c[i + j] and go(i, j + 1):
                return True
            return False
        return 'YES' if go(0, 0) else 'NO'
    return gen, sol, brute


@task('ascii_delete', 'Стереть до равенства',
"""Даны два слова. Стирая буквы из любого слова, нужно сделать их равными. Стоимость стирания буквы равна её ASCII-коду (`a` = 97, `b` = 98, …, `z` = 122; заглавные: `A` = 65, …, `Z` = 90). Какова наименьшая суммарная стоимость?

## Вход

Две строки из латинских букв, длина каждой от 1 до 1000.

## Выход

Наименьшая суммарная стоимость.""",
["sea\neat", "abc\nabc"], sizes=QUAD, diff=40)
def _():
    def gen(n, rnd, k):
        if k == 0:
            n = min(n, 7)
        al = 'abAB' if k < 6 else 'abcdefghijklmnopqrstuvwxyzXYZ'
        a = ''.join(rnd.choice(al) for _ in range(n))
        b = ''.join(rnd.choice(al) for _ in range(max(1, n + rnd.randint(-2, 2))))
        return a + '\n' + b + '\n'

    def sol(inp):
        a, b = inp.split()[:2]
        prev = [0] * (len(b) + 1)
        for i in range(1, len(a) + 1):
            cur = [0] * (len(b) + 1)
            for j in range(1, len(b) + 1):
                if a[i - 1] == b[j - 1]:
                    cur[j] = prev[j - 1] + ord(a[i - 1])
                else:
                    cur[j] = max(prev[j], cur[j - 1])
            prev = cur
        return str(sum(map(ord, a)) + sum(map(ord, b)) - 2 * prev[-1])

    def brute(inp):
        a, b = inp.split()[:2]
        subs = {}
        for m in range(1 << len(a)):
            t = ''.join(a[i] for i in range(len(a)) if m >> i & 1)
            subs[t] = sum(map(ord, t))
        best = 0
        for m in range(1 << len(b)):
            t = ''.join(b[i] for i in range(len(b)) if m >> i & 1)
            if t in subs:
                best = max(best, subs[t])
        return str(sum(map(ord, a)) + sum(map(ord, b)) - 2 * best)
    return gen, sol, brute


@task('decode_ways', 'Расшифровка цифр',
"""Сообщение зашифровано так: A = 1, B = 2, …, Z = 26, и буквы записаны подряд без разделителей. Сколькими способами можно расшифровать данную строку цифр? Числа с ведущим нулём (например `06`) буквами не являются.

## Вход

Одна строка из цифр, длина от 1 до 200000.

## Выход

Количество способов по модулю 1000000007 (0, если расшифровать нельзя).""",
["226", "06"], sizes=BIG, diff=35)
def _():
    def gen(n, rnd, k):
        w = [1, 5, 5, 1, 1, 1, 1, 1, 1, 1] if k > 3 else [1] * 10
        s = ''.join(rnd.choices('0123456789', weights=w, k=n))
        if k > 4 and rnd.random() < 0.7:
            s = ''.join(rnd.choice('1112222') + rnd.choice('0123456') for _ in range(n // 2)) or '1'
        return s + '\n'

    def sol(inp):
        s = inp.split()[0]
        M = 10 ** 9 + 7
        a, b = 1, 0
        for i, c in enumerate(s):
            cur = 0
            if c != '0':
                cur += a
            if i and s[i - 1] != '0' and int(s[i - 1:i + 1]) <= 26:
                cur += b
            cur %= M
            a, b = cur, a
        return str(a % M)

    def brute(inp):
        s = inp.split()[0]

        def go(i):
            if i == len(s):
                return 1
            if s[i] == '0':
                return 0
            r = go(i + 1)
            if i + 1 < len(s) and int(s[i:i + 2]) <= 26:
                r += go(i + 2)
            return r
        return str(go(0) % (10 ** 9 + 7))
    return gen, sol, brute


@task('ideal_subseq', 'Плавная подпоследовательность',
"""Дано слово и число k. Подпоследовательность (буквы идут в том же порядке, что в слове, но необязательно подряд) называется плавной, если для любых двух соседних её букв их номера в алфавите отличаются не более чем на k. Найдите длину самой длинной плавной подпоследовательности.

## Вход

В первой строке число k (0 ≤ k ≤ 25). Во второй строке слово из строчных латинских букв, длина от 1 до 200000.

## Выход

Длина самой длинной плавной подпоследовательности.""",
["2\nacfgbd", "0\nabcd"], sizes=BIG, diff=35)
def _():
    def gen(n, rnd, k):
        if k == 0:
            n = min(n, 11)
        kk = rnd.randint(0, 3 if k < 7 else 25)
        return str(kk) + '\n' + ''.join(rnd.choice('abcdefghijklmnopqrstuvwxyz' if k > 4 else 'abcdefg') for _ in range(n)) + '\n'

    def sol(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        best = [0] * 26
        for c in s:
            j = ord(c) - 97
            v = max(best[max(0, j - k):min(26, j + k + 1)]) + 1
            if v > best[j]:
                best[j] = v
        return str(max(best))

    def brute(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        n = len(s)
        best = 0
        for m in range(1, 1 << n):
            t = [ord(s[i]) for i in range(n) if m >> i & 1]
            if all(abs(t[i] - t[i + 1]) <= k for i in range(len(t) - 1)):
                best = max(best, len(t))
        return str(best)
    return gen, sol, brute


@task('split_three', 'Три части с равными единицами',
"""Двоичную строку разрезают на три непустые части. Сколькими способами можно сделать разрез так, чтобы в каждой части было поровну единиц?

## Вход

Одна строка из `0` и `1`, длина от 3 до 200000.

## Выход

Количество способов по модулю 1000000007.""",
["10101", "0000"], sizes=[3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000], diff=30)
def _():
    def gen(n, rnd, k):
        n = max(3, n)
        p = rnd.choice([0.05, 0.3, 0.5])
        s = ''.join('1' if rnd.random() < p else '0' for _ in range(n))
        if rnd.random() < 0.2:
            s = '0' * n
        return s + '\n'

    def sol(inp):
        s = inp.split()[0]
        M = 10 ** 9 + 7
        n = len(s)
        pos = [i for i, c in enumerate(s) if c == '1']
        c = len(pos)
        if c % 3:
            return '0'
        if c == 0:
            return str((n - 1) * (n - 2) // 2 % M)
        t = c // 3
        w1 = pos[t] - pos[t - 1]
        w2 = pos[2 * t] - pos[2 * t - 1]
        return str(w1 * w2 % M)

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        cnt = 0
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                x, y, z = s[:i].count('1'), s[i:j].count('1'), s[j:].count('1')
                if x == y == z:
                    cnt += 1
        return str(cnt % (10 ** 9 + 7))
    return gen, sol, brute
