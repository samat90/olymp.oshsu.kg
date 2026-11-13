from reg import task, LIN, MID, QUAD, SMALLQ

BIG = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]


@task('brackets3', 'Три вида скобок',
"""Строка Эрмека состоит из скобок трёх видов: круглых `()`, квадратных `[]` и фигурных `{}`. Правильна ли она? Скобки правильны, если каждая открывающая закрыта скобкой того же вида и пары не пересекаются.

## Вход

Одна строка из символов `()[]{}`, длина от 1 до 200000.

## Выход

`YES` или `NO`.""",
["([]{})", "([)]"], sizes=BIG, diff=10)
def _():
    def gen(n, rnd, k):
        pairs = ['()', '[]', '{}']
        st = []
        out = []
        for i in range(n):
            if st and (rnd.random() < 0.5 or len(st) >= n - i):
                out.append(st.pop())
            else:
                p = rnd.choice(pairs)
                out.append(p[0])
                st.append(p[1])
        while st:
            out.append(st.pop())
        if rnd.random() < 0.5:
            out[rnd.randrange(len(out))] = rnd.choice('()[]{}')
        return ''.join(out) + '\n'

    def sol(inp):
        s = inp.split()[0]
        m = {')': '(', ']': '[', '}': '{'}
        st = []
        for c in s:
            if c in '([{':
                st.append(c)
            else:
                if not st or st.pop() != m[c]:
                    return 'NO'
        return 'NO' if st else 'YES'

    def brute(inp):
        s = inp.split()[0]
        while True:
            t = s.replace('()', '').replace('[]', '').replace('{}', '')
            if t == s:
                break
            s = t
        return 'YES' if not s else 'NO'
    return gen, sol, brute


@task('add_parens', 'Достроить скобки',
"""В строке из круглых скобок можно вставлять скобки в любые места. Какое наименьшее число скобок нужно вставить, чтобы строка стала правильной скобочной последовательностью?

## Вход

Одна строка из символов `(` и `)`, длина от 1 до 200000.

## Выход

Наименьшее число вставок.""",
["())", "((("], sizes=BIG, diff=10)
def _():
    def gen(n, rnd, k):
        p = rnd.choice([0.3, 0.5, 0.7])
        return ''.join('(' if rnd.random() < p else ')' for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        bal = 0
        add = 0
        for c in s:
            if c == '(':
                bal += 1
            elif bal:
                bal -= 1
            else:
                add += 1
        return str(add + bal)

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        best = 0
        for m in range(1 << n):
            b = 0
            ok = True
            for i in range(n):
                if m >> i & 1:
                    b += 1 if s[i] == '(' else -1
                    if b < 0:
                        ok = False
                        break
            if ok and b == 0:
                best = max(best, bin(m).count('1'))
        return str(n - best)
    return gen, sol, brute


@task('longest_valid', 'Самый длинный правильный кусок',
"""Найдите самый длинный участок строки подряд, который является правильной скобочной последовательностью.

## Вход

Одна строка из символов `(` и `)`, длина от 1 до 200000.

## Выход

Длина самого длинного правильного участка (0, если такого нет).""",
[")()())", "(()"], sizes=BIG, diff=40)
def _():
    def gen(n, rnd, k):
        p = rnd.choice([0.5, 0.55, 0.45])
        return ''.join('(' if rnd.random() < p else ')' for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        st = [-1]
        best = 0
        for i, c in enumerate(s):
            if c == '(':
                st.append(i)
            else:
                st.pop()
                if not st:
                    st.append(i)
                else:
                    best = max(best, i - st[-1])
        return str(best)

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        best = 0
        for i in range(n):
            b = 0
            for j in range(i, n):
                b += 1 if s[j] == '(' else -1
                if b < 0:
                    break
                if b == 0:
                    best = max(best, j - i + 1)
        return str(best)
    return gen, sol, brute


@task('score_parens', 'Счёт скобок',
"""Счёт правильной скобочной последовательности определяется так: `()` стоит 1 очко; запись `AB` стоит столько, сколько A плюс B; запись `(A)` стоит вдвое больше, чем A. Найдите счёт данной последовательности.

## Вход

Одна правильная скобочная последовательность длиной от 2 до 200000.

## Выход

Счёт по модулю 1000000007.""",
["(())", "()(())"], sizes=BIG, diff=30)
def _():
    def gen(n, rnd, k):
        n = max(2, n - n % 2)
        pr = rnd.choice([0.5, 0.6])
        out = []
        o = 0
        for i in range(n):
            left = n - i
            if o == left:
                out.append(')')
                o -= 1
            elif o == 0 or rnd.random() < pr:
                out.append('(')
                o += 1
            else:
                out.append(')')
                o -= 1
        return ''.join(out) + '\n'

    def sol(inp):
        s = inp.split()[0]
        M = 10 ** 9 + 7
        st = [0]
        for c in s:
            if c == '(':
                st.append(0)
            else:
                v = st.pop()
                st[-1] = (st[-1] + (1 if v == 0 else 2 * v)) % M
        return str(st[0] % M)

    def brute(inp):
        s = inp.split()[0]
        M = 10 ** 9 + 7

        def f(l, r):
            if l >= r:
                return 0
            b = 0
            for i in range(l, r):
                b += 1 if s[i] == '(' else -1
                if b == 0:
                    inner = f(l + 1, i)
                    return ((1 if inner == 0 else 2 * inner) + f(i + 1, r)) % M
        return str(f(0, len(s)) % M)
    return gen, sol, brute


@task('remove_outer', 'Снять внешние скобки',
"""Правильную скобочную последовательность можно разбить на неразложимые части (каждая заканчивается там, где баланс впервые становится нулём). У каждой части снимите внешнюю пару скобок и запишите результаты подряд.

## Вход

Одна правильная скобочная последовательность длиной от 2 до 200000.

## Выход

Получившаяся строка (если она пуста, выведите пустую строку).""",
["(()())(())", "()()"], sizes=BIG, diff=15)
def _():
    def gen(n, rnd, k):
        n = max(4, n - n % 2) if k else n
        n = max(2, n - n % 2)
        out = []
        o = 0
        for i in range(n):
            left = n - i
            if o == left:
                out.append(')')
                o -= 1
            elif o == 0 or rnd.random() < 0.55:
                out.append('(')
                o += 1
            else:
                out.append(')')
                o -= 1
        return ''.join(out) + '\n'

    def sol(inp):
        s = inp.split()[0]
        res = []
        b = 0
        for c in s:
            if c == '(':
                if b:
                    res.append(c)
                b += 1
            else:
                b -= 1
                if b:
                    res.append(c)
        return ''.join(res)

    def brute(inp):
        s = inp.split()[0]
        parts = []
        b = 0
        st = 0
        for i, c in enumerate(s):
            b += 1 if c == '(' else -1
            if b == 0:
                parts.append(s[st + 1:i])
                st = i + 1
        return ''.join(parts)
    return gen, sol, brute


@task('remove_pairs', 'Убрать пары',
"""Пока в слове есть две одинаковые соседние буквы, их можно вычеркнуть (оба символа). Что останется в конце? Результат не зависит от порядка вычёркиваний.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Оставшаяся строка или `-`, если ничего не осталось.""",
["abbaca", "aa"], sizes=BIG, diff=15)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 5 else 'abc'
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        st = []
        for c in s:
            if st and st[-1] == c:
                st.pop()
            else:
                st.append(c)
        return ''.join(st) or '-'

    def brute(inp):
        s = inp.split()[0]
        ch = True
        while ch:
            ch = False
            for i in range(len(s) - 1):
                if s[i] == s[i + 1]:
                    s = s[:i] + s[i + 2:]
                    ch = True
                    break
        return s or '-'
    return gen, sol, brute


@task('remove_k_equal', 'Убрать k одинаковых',
"""Пока в слове есть k одинаковых букв подряд, их можно вычеркнуть, и оставшиеся части склеиваются. Что останется в конце? Результат не зависит от порядка вычёркиваний.

## Вход

В первой строке число k (2 ≤ k ≤ 200000). Во второй строке слово из строчных латинских букв, длина от 1 до 200000.

## Выход

Оставшаяся строка или `-`, если ничего не осталось.""",
["2\nabbaca", "3\ndeeedbbcccbdaa"], sizes=BIG, diff=30)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 6 else 'abc'
        kk = rnd.randint(2, 4)
        return str(kk) + '\n' + ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        st = []
        for c in s:
            if st and st[-1][0] == c:
                st[-1][1] += 1
                if st[-1][1] == k:
                    st.pop()
            else:
                st.append([c, 1])
        return ''.join(c * m for c, m in st) or '-'

    def brute(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        ch = True
        while ch:
            ch = False
            for i in range(len(s) - k + 1):
                if s[i:i + k] == s[i] * k:
                    s = s[:i] + s[i + k:]
                    ch = True
                    break
        return s or '-'
    return gen, sol, brute


@task('decode_len', 'Длина распакованной строки',
"""Строка упакована так: запись `m[X]` означает, что слово X повторено m раз (m — число от 1 до 9, X может содержать вложенные записи). Буквы вне скобок записаны как есть. Найдите длину распакованной строки.

## Вход

Одна упакованная строка длиной от 1 до 200000 из строчных латинских букв, цифр 1–9 и скобок `[]`. Запись всегда правильная.

## Выход

Длина распакованной строки по модулю 1000000007.""",
["3[a]2[bc]", "2[3[x]y]"], sizes=BIG, diff=35)
def _():
    def gen(n, rnd, k):
        import sys
        sys.setrecursionlimit(10000)
        mx = 3 if k == 0 else 9

        def ex(b):
            out = []
            while b > 0:
                if b >= 5 and rnd.random() < 0.4:
                    inner = rnd.randint(1, min(b - 4, max(1, b // 2)))
                    out.append(str(rnd.randint(1, mx)) + '[' + ex(inner) + ']')
                    b -= inner + 3
                else:
                    out.append(rnd.choice('abc'))
                    b -= 1
            return ''.join(out)
        if k >= 5:
            parts = []
            tot = 0
            while tot < n:
                seg = min(n - tot, rnd.randint(5, 200))
                s = ex(seg)
                parts.append(s)
                tot += len(s) + 1
            s = ''.join(parts)
        else:
            s = ex(n)
        return (s or 'a') + '\n'

    def sol(inp):
        s = inp.split()[0]
        M = 10 ** 9 + 7
        st = [[0, 1]]
        num = 1
        for c in s:
            if c.isdigit():
                num = int(c)
            elif c == '[':
                st.append([0, num])
                num = 1
            elif c == ']':
                v, m = st.pop()
                st[-1][0] = (st[-1][0] + v * m) % M
            else:
                st[-1][0] = (st[-1][0] + 1) % M
        return str(st[0][0] % M)

    def brute(inp):
        s = inp.split()[0]
        M = 10 ** 9 + 7

        def parse(i):
            res = ''
            while i < len(s) and s[i] != ']':
                if s[i].isdigit():
                    m = int(s[i])
                    sub, i = parse(i + 2)
                    res += sub * m
                    i += 1
                else:
                    res += s[i]
                    i += 1
            return res, i
        return str(len(parse(0)[0]) % M)
    return gen, sol, brute


@task('reverse_in_parens', 'Перевороты в скобках',
"""В строке есть вложенные круглые скобки. Все буквы внутри каждой пары скобок нужно развернуть (сначала самые внутренние пары), а сами скобки убрать. Выведите результат.

## Вход

Одна строка из строчных латинских букв и круглых скобок, длина от 1 до 200000. Скобки правильные.

## Выход

Получившееся слово (если букв нет, выведите пустую строку).""",
["(ed(et)o)", "a(bc)d"], sizes=BIG, diff=45)
def _():
    def gen(n, rnd, k):
        out = []
        o = 0
        for i in range(n):
            left = n - i
            if o == left:
                out.append(')')
                o -= 1
                continue
            r = rnd.random()
            if r < 0.15 and left > o + 1:
                out.append('(')
                o += 1
            elif r < 0.3 and o:
                out.append(')')
                o -= 1
            else:
                out.append(rnd.choice('abcdef'))
        s = ''.join(out)
        return (s if any(c.isalpha() for c in s) else 'a' + s) + '\n'

    def sol(inp):
        s = inp.split()[0]
        n = len(s)
        match = [0] * n
        st = []
        for i, c in enumerate(s):
            if c == '(':
                st.append(i)
            elif c == ')':
                j = st.pop()
                match[i] = j
                match[j] = i
        res = []
        i = 0
        d = 1
        while 0 <= i < n:
            if s[i] in '()':
                i = match[i]
                d = -d
            else:
                res.append(s[i])
            i += d
        return ''.join(res)

    def brute(inp):
        s = inp.split()[0]
        st = ['']
        for c in s:
            if c == '(':
                st.append('')
            elif c == ')':
                t = st.pop()
                st[-1] += t[::-1]
            else:
                st[-1] += c
        return st[0]
    return gen, sol, brute


@task('bracket_swaps', 'Обмены скобок',
"""В строке поровну открывающих `[` и закрывающих `]` квадратных скобок. За один ход можно поменять местами любые две скобки строки. Какое наименьшее число ходов делает строку правильной скобочной последовательностью?

## Вход

Одна строка из `[` и `]` чётной длины от 2 до 200000, в которой скобок каждого вида поровну.

## Выход

Наименьшее число ходов.""",
["]][[", "[]"], sizes=BIG, diff=40)
def _():
    def gen(n, rnd, k):
        n = max(2, n - n % 2)
        s = ['['] * (n // 2) + [']'] * (n // 2)
        rnd.shuffle(s)
        return ''.join(s) + '\n'

    def sol(inp):
        s = inp.split()[0]
        b = 0
        un = 0
        for c in s:
            if c == '[':
                b += 1
            elif b:
                b -= 1
            else:
                un += 1
        return str((un + 1) // 2)

    def brute(inp):
        s = inp.split()[0]
        from collections import deque

        def ok(t):
            b = 0
            for c in t:
                b += 1 if c == '[' else -1
                if b < 0:
                    return False
            return b == 0
        d = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            if ok(u):
                return str(d[u])
            for i in range(len(u)):
                for j in range(i + 1, len(u)):
                    if u[i] != u[j]:
                        v = list(u)
                        v[i], v[j] = v[j], v[i]
                        v = ''.join(v)
                        if v not in d:
                            d[v] = d[u] + 1
                            q.append(v)
    return gen, sol, brute


@task('fill_brackets', 'Заполнить вопросы',
"""В строке есть открывающие скобки `(`, закрывающие `)` и знаки `?`. Каждый знак `?` нужно заменить на `(` или `)`. Сколькими способами можно получить правильную скобочную последовательность?

## Вход

Одна строка из символов `(`, `)`, `?` длиной от 1 до 1000.

## Выход

Количество способов по модулю 1000000007.""",
["(?)?", "))"], sizes=SMALLQ, diff=40)
def _():
    def gen(n, rnd, k):
        if k == 0:
            n = min(n, 10)
        w = rnd.choice([(3, 3, 4), (1, 1, 8), (4, 2, 2)])
        return ''.join(rnd.choices('()?', weights=w, k=n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        M = 10 ** 9 + 7
        n = len(s)
        dp = [0] * (n + 2)
        dp[0] = 1
        for c in s:
            nd = [0] * (n + 2)
            for b in range(n + 1):
                v = dp[b]
                if not v:
                    continue
                if c in '(?':
                    nd[b + 1] = (nd[b + 1] + v) % M
                if c in ')?' and b:
                    nd[b - 1] = (nd[b - 1] + v) % M
            dp = nd
        return str(dp[0] % M)

    def brute(inp):
        s = inp.split()[0]
        pos = [i for i, c in enumerate(s) if c == '?']
        cnt = 0
        for m in range(1 << len(pos)):
            t = list(s)
            for j, p in enumerate(pos):
                t[p] = '(' if m >> j & 1 else ')'
            b = 0
            ok = True
            for c in t:
                b += 1 if c == '(' else -1
                if b < 0:
                    ok = False
                    break
            if ok and b == 0:
                cnt += 1
        return str(cnt % (10 ** 9 + 7))
    return gen, sol, brute


@task('kth_brackets', 'k-я скобочная последовательность',
"""Все правильные скобочные последовательности из n пар скобок выписаны в лексикографическом порядке, при этом `(` считается меньше `)`. Найдите k-ю по счёту.

## Вход

Два числа n и k через пробел (1 ≤ n ≤ 30, 1 ≤ k ≤ 10^16).

## Выход

k-я последовательность или `-1`, если их меньше k.""",
["3 4", "2 3"], sizes=[1, 2, 3, 5, 8, 12, 18, 24, 28, 30], diff=55)
def _():
    def gen(n, rnd, k):
        if k == 0:
            n = min(n, 8)
        C = [1]
        for i in range(1, n + 1):
            C.append(C[-1] * 2 * (2 * i - 1) // (i + 1))
        total = C[n]
        r = rnd.random()
        if r < 0.1:
            kk = total + rnd.randint(1, 3)
        elif r < 0.2:
            kk = total
        else:
            kk = rnd.randint(1, total)
        kk = min(kk, 10 ** 16)
        return '%d %d\n' % (n, kk)

    def sol(inp):
        n, k = map(int, inp.split()[:2])
        # f[r][o]: ways to finish with r chars left and o open
        f = [[0] * (n + 2) for _ in range(2 * n + 1)]
        f[0][0] = 1
        for r in range(1, 2 * n + 1):
            for o in range(0, n + 1):
                v = f[r - 1][o + 1] if o + 1 <= n else 0
                if o > 0:
                    v += f[r - 1][o - 1]
                f[r][o] = v
        if f[2 * n][0] < k:
            return '-1'
        res = []
        o = 0
        for i in range(2 * n):
            r = 2 * n - i - 1
            # try '('
            if o + 1 <= n and f[r][o + 1] >= k:
                res.append('(')
                o += 1
            else:
                if o + 1 <= n:
                    k -= f[r][o + 1]
                res.append(')')
                o -= 1
        return ''.join(res)

    def brute(inp):
        n, k = map(int, inp.split()[:2])
        res = []

        def go(s, o, c):
            if len(s) == 2 * n:
                res.append(s)
                return
            if o < n:
                go(s + '(', o + 1, c)
            if c < o:
                go(s + ')', o, c + 1)
        go('', 0, 0)
        res.sort()
        return res[k - 1] if k <= len(res) else '-1'
    return gen, sol, brute
