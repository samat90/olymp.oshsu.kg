from reg import task, LIN, MID, QUAD, SMALLQ


@task('longest_no_repeat', 'Без повторов',
"""Тынчтык ищет в слове самый длинный участок подряд, в котором все буквы различны.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Длина самого длинного участка без повторяющихся букв.""",
["abcabcbb", "bbbb"], diff=20)
def _():
    def gen(n, rnd, k):
        al = 'abc' if k == 0 else ('abcdefghijklmnopqrstuvwxyz' if k > 3 else 'abcdef')
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        last = {}
        st = 0
        best = 0
        for i, c in enumerate(s):
            if c in last and last[c] >= st:
                st = last[c] + 1
            last[c] = i
            if i - st + 1 > best:
                best = i - st + 1
        return str(best)

    def brute(inp):
        s = inp.split()[0]
        best = 0
        for i in range(len(s)):
            for j in range(i, len(s)):
                t = s[i:j + 1]
                if len(set(t)) == len(t):
                    best = max(best, len(t))
        return str(best)
    return gen, sol, brute


@task('longest_k_distinct', 'Не более k разных',
"""Дан текст и число k. Найдите самый длинный участок подряд, в котором встречается не более k различных букв.

## Вход

В первой строке число k (1 ≤ k ≤ 26). Во второй строке текст из строчных латинских букв, длина от 1 до 200000.

## Выход

Длина самого длинного такого участка.""",
["2\neceba", "1\naabbb"], diff=25)
def _():
    def gen(n, rnd, k):
        kk = rnd.randint(1, 3 if k < 8 else 26)
        al = 'abcde' if k < 8 else 'abcdefghijklmnopqrstuvwxyz'
        return str(kk) + '\n' + ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        cnt = {}
        l = 0
        best = 0
        for r, c in enumerate(s):
            cnt[c] = cnt.get(c, 0) + 1
            while len(cnt) > k:
                d = s[l]
                cnt[d] -= 1
                if cnt[d] == 0:
                    del cnt[d]
                l += 1
            best = max(best, r - l + 1)
        return str(best)

    def brute(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        best = 0
        for i in range(len(s)):
            for j in range(i, len(s)):
                if len(set(s[i:j + 1])) <= k:
                    best = max(best, j - i + 1)
        return str(best)
    return gen, sol, brute


@task('char_replacement', 'Покрасить в одну букву',
"""Можно заменить не более k букв слова на любые другие. Какой наибольшей длины участок подряд можно сделать состоящим из одной и той же буквы?

## Вход

В первой строке число k (0 ≤ k ≤ 200000). Во второй строке слово из заглавных латинских букв, длина от 1 до 200000.

## Выход

Наибольшая длина участка.""",
["1\nAABABBA", "0\nABC"], diff=40)
def _():
    def gen(n, rnd, k):
        al = 'AB' if k < 5 else 'ABCDE'
        kk = rnd.randint(0, 3 if k < 7 else n // 3 + 1)
        return str(kk) + '\n' + ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        cnt = [0] * 26
        l = 0
        mx = 0
        best = 0
        for r, c in enumerate(s):
            j = ord(c) - 65
            cnt[j] += 1
            mx = max(mx, cnt[j])
            if r - l + 1 - mx > k:
                cnt[ord(s[l]) - 65] -= 1
                l += 1
            best = max(best, r - l + 1)
        return str(best)

    def brute(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        best = 0
        for i in range(len(s)):
            for j in range(i, len(s)):
                t = s[i:j + 1]
                if len(t) - max(t.count(c) for c in set(t)) <= k:
                    best = max(best, len(t))
        return str(best)
    return gen, sol, brute


@task('min_window', 'Кратчайший участок',
"""Даны текст и набор букв (буквы могут повторяться). Найдите кратчайший участок текста подряд, который содержит каждую букву набора не меньше раз, чем она встречается в наборе.

## Вход

Первая строка — текст, вторая — набор. Обе из строчных латинских букв, длина каждой от 1 до 200000.

## Выход

Длина кратчайшего участка или `-1`, если такого участка нет.""",
["adobecodebanc\nabc", "a\naa"], diff=45)
def _():
    def gen(n, rnd, k):
        al = 'abc' if k < 6 else 'abcdefgh'
        m = rnd.randint(1, 4 if k < 6 else max(2, min(n // 3, 20)))
        t = ''.join(rnd.choice(al) for _ in range(m))
        s = ''.join(rnd.choice(al) for _ in range(n))
        if k > 6 and rnd.random() < 0.8:
            q = list(s)
            for c in t:
                q[rnd.randrange(n)] = c
            s = ''.join(q)
        return s + '\n' + t + '\n'

    def sol(inp):
        s, t = inp.split()[:2]
        need = {}
        for c in t:
            need[c] = need.get(c, 0) + 1
        miss = len(t)
        have = {}
        l = 0
        best = -1
        for r, c in enumerate(s):
            if c in need:
                have[c] = have.get(c, 0) + 1
                if have[c] <= need[c]:
                    miss -= 1
            while miss == 0:
                if best == -1 or r - l + 1 < best:
                    best = r - l + 1
                d = s[l]
                if d in need:
                    have[d] -= 1
                    if have[d] < need[d]:
                        miss += 1
                l += 1
        return str(best)

    def brute(inp):
        s, t = inp.split()[:2]
        best = -1
        for i in range(len(s)):
            for j in range(i, len(s)):
                w = s[i:j + 1]
                if all(w.count(c) >= t.count(c) for c in set(t)):
                    if best == -1 or len(w) < best:
                        best = len(w)
                    break
        return str(best)
    return gen, sol, brute


@task('substr_abc', 'Три буквы',
"""Сколько подстрок слова содержат каждую из букв `a`, `b` и `c` хотя бы по разу? Подстроки с разными позициями считаются разными.

## Вход

Одна строка из букв `a`, `b`, `c`, длина от 1 до 200000.

## Выход

Количество подстрок.""",
["abcabc", "aaabb"], diff=30)
def _():
    def gen(n, rnd, k):
        return ''.join(rnd.choice('abc') for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        last = [-1, -1, -1]
        ans = 0
        for i, c in enumerate(s):
            last[ord(c) - 97] = i
            ans += min(last) + 1
        return str(ans)

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        return str(sum(1 for i in range(n) for j in range(i, n) if len(set(s[i:j + 1])) == 3))
    return gen, sol, brute


@task('substr_exact_k', 'Ровно k разных',
"""Сколько подстрок слова содержат ровно k различных букв? Подстроки с разными позициями считаются разными.

## Вход

В первой строке число k (1 ≤ k ≤ 26). Во второй строке слово из строчных латинских букв, длина от 1 до 200000.

## Выход

Количество подстрок.""",
["2\nabaab", "3\nabab"], diff=45)
def _():
    def gen(n, rnd, k):
        al = 'abc' if k < 4 else 'abcdefghij'
        kk = rnd.randint(1, 3 if k < 6 else 6)
        return str(kk) + '\n' + ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]

        def most(m):
            if m == 0:
                return 0
            cnt = {}
            l = 0
            res = 0
            for r, c in enumerate(s):
                cnt[c] = cnt.get(c, 0) + 1
                while len(cnt) > m:
                    d = s[l]
                    cnt[d] -= 1
                    if cnt[d] == 0:
                        del cnt[d]
                    l += 1
                res += r - l + 1
            return res
        return str(most(k) - most(k - 1))

    def brute(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        n = len(s)
        return str(sum(1 for i in range(n) for j in range(i, n) if len(set(s[i:j + 1])) == k))
    return gen, sol, brute


@task('equal_ab', 'Поровну a и b',
"""Найдите самый длинный участок слова подряд, в котором букв `a` и `b` поровну (букв `c` может быть сколько угодно).

## Вход

Одна строка из букв `a`, `b`, `c`, длина от 1 до 200000.

## Выход

Длина самого длинного участка (если таких нет, выведите 0).""",
["abcc", "aab"], diff=35)
def _():
    def gen(n, rnd, k):
        w = [3, 3, rnd.choice([0, 1, 3])]
        return ''.join(rnd.choices('abc', weights=w, k=n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        first = {0: -1}
        d = 0
        best = 0
        for i, c in enumerate(s):
            if c == 'a':
                d += 1
            elif c == 'b':
                d -= 1
            if d in first:
                best = max(best, i - first[d])
            else:
                first[d] = i
        return str(best)

    def brute(inp):
        s = inp.split()[0]
        best = 0
        for i in range(len(s)):
            for j in range(i, len(s)):
                t = s[i:j + 1]
                if t.count('a') == t.count('b'):
                    best = max(best, len(t))
        return str(best)
    return gen, sol, brute


@task('vowels_even', 'Чётные гласные',
"""Найдите самый длинный участок слова подряд, в котором каждая из гласных `a`, `e`, `i`, `o`, `u` встречается чётное число раз (ноль раз тоже чётно).

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Длина самого длинного участка.""",
["eleetminicoworoep", "bcbcbc"], diff=45)
def _():
    def gen(n, rnd, k):
        al = 'aeiouxyz' if k > 3 else 'aebxy'
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        bit = {'a': 1, 'e': 2, 'i': 4, 'o': 8, 'u': 16}
        first = {0: -1}
        m = 0
        best = 0
        for i, c in enumerate(s):
            m ^= bit.get(c, 0)
            if m in first:
                best = max(best, i - first[m])
            else:
                first[m] = i
        return str(best)

    def brute(inp):
        s = inp.split()[0]
        best = 0
        for i in range(len(s)):
            for j in range(i, len(s)):
                t = s[i:j + 1]
                if all(t.count(v) % 2 == 0 for v in 'aeiou'):
                    best = max(best, len(t))
        return str(best)
    return gen, sol, brute


@task('binary_k_ones', 'Подстроки с k единицами',
"""Сколько подстрок двоичной строки содержат ровно k единиц? Подстроки с разными позициями считаются разными.

## Вход

В первой строке число k (0 ≤ k ≤ 200000). Во второй строке строка из символов `0` и `1`, длина от 1 до 200000.

## Выход

Количество подстрок.""",
["2\n1010101", "0\n00100"], diff=25)
def _():
    def gen(n, rnd, k):
        p = rnd.choice([0.1, 0.3, 0.5, 0.8])
        s = ''.join('1' if rnd.random() < p else '0' for _ in range(n))
        kk = rnd.randint(0, 3 if k < 5 else max(1, int(n * p / 3)))
        return str(kk) + '\n' + s + '\n'

    def sol(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        cnt = {0: 1}
        pre = 0
        ans = 0
        for c in s:
            if c == '1':
                pre += 1
            ans += cnt.get(pre - k, 0)
            cnt[pre] = cnt.get(pre, 0) + 1
        return str(ans)

    def brute(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        n = len(s)
        return str(sum(1 for i in range(n) for j in range(i, n) if s[i:j + 1].count('1') == k))
    return gen, sol, brute


@task('max_vowels', 'Много гласных',
"""Дано слово и число k. Среди всех участков слова длины k найдите тот, в котором больше всего гласных (`a`, `e`, `i`, `o`, `u`).

## Вход

В первой строке число k. Во второй строке слово из строчных латинских букв, длина n (1 ≤ k ≤ n ≤ 200000).

## Выход

Наибольшее число гласных в участке длины k.""",
["3\nabciiidef", "2\nrhythm"], diff=10)
def _():
    def gen(n, rnd, k):
        al = 'aeioubcdfg' if k else 'aebc'
        return str(rnd.randint(1, n)) + '\n' + ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        v = 'aeiou'
        cur = sum(1 for c in s[:k] if c in v)
        best = cur
        for i in range(k, len(s)):
            cur += (s[i] in v) - (s[i - k] in v)
            best = max(best, cur)
        return str(best)

    def brute(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        return str(max(sum(1 for c in s[i:i + k] if c in 'aeiou') for i in range(len(s) - k + 1)))
    return gen, sol, brute


@task('common_substring', 'Общий кусок',
"""Даны два слова. Найдите длину самой длинной строки, которая является подстрокой (участком подряд) обоих слов.

## Вход

Две строки из строчных латинских букв, длина каждой от 1 до 1000.

## Выход

Длина самой длинной общей подстроки (0, если общих букв нет).""",
["alatoo\nlatoon", "abc\nxyz"], sizes=QUAD, diff=35)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 5 else 'abcd'
        a = ''.join(rnd.choice(al) for _ in range(n))
        b = ''.join(rnd.choice(al) for _ in range(max(1, n + rnd.randint(-2, 2))))
        return a + '\n' + b + '\n'

    def sol(inp):
        a, b = inp.split()[:2]
        best = 0
        prev = [0] * (len(b) + 1)
        for i in range(1, len(a) + 1):
            cur = [0] * (len(b) + 1)
            for j in range(1, len(b) + 1):
                if a[i - 1] == b[j - 1]:
                    cur[j] = prev[j - 1] + 1
                    if cur[j] > best:
                        best = cur[j]
            prev = cur
        return str(best)

    def brute(inp):
        a, b = inp.split()[:2]
        best = 0
        for i in range(len(a)):
            for j in range(i + 1, len(a) + 1):
                if a[i:j] in b:
                    best = max(best, j - i)
        return str(best)
    return gen, sol, brute


@task('common_prefix', 'Общее начало',
"""Асан записал n слов. Найдите самое длинное слово, с которого начинаются все они.

## Вход

В первой строке число n (1 ≤ n ≤ 100000). Затем n строк, в каждой слово из строчных латинских букв. Суммарная длина слов не больше 300000.

## Выход

Самый длинный общий префикс или `-`, если он пуст.""",
["3\nkarakol\nkara\nkarabalta", "2\nosh\nnaryn"],
sizes=[3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000], diff=10)
def _():
    def gen(n, rnd, k):
        base = ''.join(rnd.choice('ab') for _ in range(rnd.randint(0, min(5 if k < 8 else 100, max(1, 250000 // n - 3)))))
        ws = []
        for _ in range(n):
            ws.append(base + ''.join(rnd.choice('ab') for _ in range(rnd.randint(0 if base else 1, 2 if k < 8 else 1))))
        return str(n) + '\n' + '\n'.join(ws) + '\n'

    def sol(inp):
        a = inp.split()
        n = int(a[0])
        ws = a[1:n + 1]
        lo, hi = min(ws), max(ws)
        i = 0
        while i < len(lo) and lo[i] == hi[i]:
            i += 1
        return lo[:i] if i else '-'

    def brute(inp):
        a = inp.split()
        n = int(a[0])
        ws = a[1:n + 1]
        p = ws[0]
        for w in ws[1:]:
            while not w.startswith(p):
                p = p[:-1]
        return p if p else '-'
    return gen, sol, brute


@task('lcs_len', 'Общая подпоследовательность',
"""Даны два слова. Найдите длину самой длинной общей подпоследовательности: набора букв, которые идут в обоих словах в одном порядке (не обязательно подряд).

## Вход

Две строки из строчных латинских букв, длина каждой от 1 до 1000.

## Выход

Длина самой длинной общей подпоследовательности.""",
["manas\nmanasa", "abc\ndef"], sizes=QUAD, diff=35)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 5 else 'abcde'
        n = min(n, 10) if k == 0 else n
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
                    cur[j] = prev[j - 1] + 1
                else:
                    cur[j] = max(prev[j], cur[j - 1])
            prev = cur
        return str(prev[-1])

    def brute(inp):
        a, b = inp.split()[:2]
        best = 0
        subs = set()
        for m in range(1 << len(a)):
            subs.add(''.join(a[i] for i in range(len(a)) if m >> i & 1))
        for m in range(1 << len(b)):
            t = ''.join(b[i] for i in range(len(b)) if m >> i & 1)
            if t in subs:
                best = max(best, len(t))
        return str(best)
    return gen, sol, brute


@task('subseq_words', 'Слова-подпоследовательности',
"""Дана длинная строка s и список слов. Сколько слов списка являются подпоследовательностями s (получаются из s вычёркиванием некоторых букв)? Одинаковые слова в списке считаются отдельно.

## Вход

В первой строке строка s из строчных латинских букв, длина от 1 до 100000. Во второй строке число слов m (1 ≤ m ≤ 20000). Затем m строк со словами из строчных латинских букв. Суммарная длина слов не больше 100000.

## Выход

Количество слов, являющихся подпоследовательностями s.""",
["abcde\n3\nace\naec\nabcde"], sizes=[3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000], diff=40)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 5 else 'abcde'
        s = ''.join(rnd.choice(al) for _ in range(n))
        m = min(20000, n)
        ws = []
        tot = 0
        for _ in range(m):
            ln = rnd.randint(1, min(4 if k < 5 else 8, max(1, 100000 // m)))
            ws.append(''.join(rnd.choice(al) for _ in range(ln)))
        return s + '\n' + str(m) + '\n' + '\n'.join(ws) + '\n'

    def sol(inp):
        a = inp.split()
        s = a[0]
        m = int(a[1])
        from bisect import bisect_right
        pos = {}
        for i, c in enumerate(s):
            pos.setdefault(c, []).append(i)
        res = 0
        for w in a[2:2 + m]:
            p = -1
            ok = True
            for c in w:
                l = pos.get(c)
                if not l:
                    ok = False
                    break
                j = bisect_right(l, p)
                if j == len(l):
                    ok = False
                    break
                p = l[j]
            res += ok
        return str(res)

    def brute(inp):
        a = inp.split()
        s = a[0]
        m = int(a[1])
        res = 0
        for w in a[2:2 + m]:
            it = iter(s)
            res += all(c in it for c in w)
        return str(res)
    return gen, sol, brute


@task('distinct_subseq', 'Разные подпоследовательности',
"""Сколько различных непустых подпоследовательностей у слова? Подпоследовательность получается вычёркиванием некоторых букв; одинаковые слова, полученные разными способами, считаются один раз.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Количество по модулю 1000000007.""",
["abc", "aaa"], diff=55)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 5 else 'abcdefghijklmnopqrstuvwxyz'
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        M = 10 ** 9 + 7
        end = [0] * 26
        tot = 1
        for c in s:
            j = ord(c) - 97
            nt = (2 * tot - end[j]) % M
            end[j] = tot
            tot = nt
        return str((tot - 1) % M)

    def brute(inp):
        s = inp.split()[0]
        st = set()
        for m in range(1, 1 << len(s)):
            st.add(''.join(s[i] for i in range(len(s)) if m >> i & 1))
        return str(len(st) % (10 ** 9 + 7))
    return gen, sol, brute


@task('count_subseq', 'Сколько способов вычеркнуть',
"""Сколькими способами из слова s можно вычеркнуть буквы так, чтобы осталось слово t? Способы различаются набором оставленных позиций.

## Вход

Две строки из строчных латинских букв: s и t, 1 ≤ |t| ≤ |s| ≤ 1500.

## Выход

Количество способов по модулю 1000000007.""",
["rabbbit\nrabbit", "abc\nd"], sizes=[3, 8, 15, 50, 100, 300, 600, 1000, 1500, 1500], diff=40)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 8 else 'abc'
        s = ''.join(rnd.choice(al) for _ in range(n))
        m = rnd.randint(1, max(1, min(n, 4 if k == 0 else n // 2 + 1)))
        t = ''.join(rnd.choice(al) for _ in range(m))
        return s + '\n' + t + '\n'

    def sol(inp):
        s, t = inp.split()[:2]
        M = 10 ** 9 + 7
        dp = [0] * (len(t) + 1)
        dp[0] = 1
        for c in s:
            for j in range(len(t), 0, -1):
                if t[j - 1] == c:
                    dp[j] = (dp[j] + dp[j - 1]) % M
        return str(dp[len(t)])

    def brute(inp):
        s, t = inp.split()[:2]
        n = len(s)
        cnt = 0
        for m in range(1 << n):
            if bin(m).count('1') == len(t) and ''.join(s[i] for i in range(n) if m >> i & 1) == t:
                cnt += 1
        return str(cnt % (10 ** 9 + 7))
    return gen, sol, brute


@task('edit_distance', 'Исправление слова',
"""За один ход слово меняют одним из трёх способов: вставляют букву в любое место, удаляют любую букву или заменяют любую букву другой. За какое наименьшее число ходов слово Умута станет словом Лейлек?

## Вход

Две строки из строчных латинских букв, длина каждой от 1 до 800.

## Выход

Наименьшее число ходов.""",
["horse\nros", "osh\nosh"], sizes=[3, 8, 15, 50, 100, 200, 400, 600, 800, 800], diff=40)
def _():
    def gen(n, rnd, k):
        if k == 0:
            n = min(n, 6)
        al = 'ab' if k < 6 else 'abcdef'
        a = ''.join(rnd.choice(al) for _ in range(n))
        b = list(a)
        for _ in range(rnd.randint(0, 3 if k else 2)):
            r = rnd.random()
            if r < 0.3 and b:
                b.pop(rnd.randrange(len(b)))
            elif r < 0.6:
                b.insert(rnd.randint(0, len(b)), rnd.choice(al))
            elif b:
                b[rnd.randrange(len(b))] = rnd.choice(al)
        if rnd.random() < 0.3 or not b:
            b = [rnd.choice(al) for _ in range(max(1, n))]
        return a + '\n' + ''.join(b) + '\n'

    def sol(inp):
        a, b = inp.split()[:2]
        prev = list(range(len(b) + 1))
        for i in range(1, len(a) + 1):
            cur = [i] + [0] * len(b)
            for j in range(1, len(b) + 1):
                cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1]))
            prev = cur
        return str(prev[-1])

    def brute(inp):
        a, b = inp.split()[:2]
        from collections import deque
        al = sorted(set(a + b))
        lim = max(len(a), len(b)) + 1
        d = {a: 0}
        q = deque([a])
        while q:
            u = q.popleft()
            if u == b:
                return str(d[u])
            nb = []
            for i in range(len(u)):
                nb.append(u[:i] + u[i + 1:])
                for c in al:
                    if c != u[i]:
                        nb.append(u[:i] + c + u[i + 1:])
            if len(u) < lim:
                for i in range(len(u) + 1):
                    for c in al:
                        nb.append(u[:i] + c + u[i:])
            for v in nb:
                if v not in d:
                    d[v] = d[u] + 1
                    q.append(v)
    return gen, sol, brute
