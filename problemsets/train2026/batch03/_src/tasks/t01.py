from reg import task, LIN, MID, QUAD, SMALLQ


@task('pal_clean', 'Чистый палиндром',
"""Айбек записал фразу на табличке. Он считает, что фраза читается одинаково в обе стороны, если учитывать только латинские буквы и цифры, а регистр букв не важен.

Проверьте, так ли это.

## Вход

Одна строка длиной не более 200000 символов: латинские буквы, цифры, пробелы и знаки препинания. В строке есть хотя бы одна буква или цифра.

## Выход

`YES`, если фраза читается одинаково в обе стороны, иначе `NO`.""",
["Naryn: nyran", "Osh-Osh"], sizes=LIN, diff=10)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k == 0 else 'abcxyzABC0189'
        h = ''.join(rnd.choice(al) for _ in range(max(1, n // 2)))
        s = list(h + rnd.choice(['', 'a', 'Z']) + h[::-1])
        if rnd.random() < 0.5:
            s[rnd.randrange(len(s))] = rnd.choice(al)
        out = []
        for c in s:
            while rnd.random() < 0.3:
                out.append(rnd.choice(' ,.:!-'))
            out.append(c.swapcase() if rnd.random() < 0.4 else c)
        r = ''.join(out).strip()
        return (r if any(c.isalnum() for c in r) else 'a') + '\n'

    def sol(inp):
        s = inp.split('\n')[0].rstrip('\r')
        t = [c.lower() for c in s if c.isalnum()]
        return 'YES' if t == t[::-1] else 'NO'

    def brute(inp):
        s = inp.split('\n')[0].rstrip('\r')
        t = ''.join(c for c in s if c.isalnum()).lower()
        i, j = 0, len(t) - 1
        while i < j:
            if t[i] != t[j]:
                return 'NO'
            i += 1
            j -= 1
        return 'YES'
    return gen, sol, brute


@task('pal_almost', 'Почти палиндром',
"""Бермет может стереть из слова не более одной буквы. Можно ли после этого получить палиндром (слово, которое читается одинаково слева направо и справа налево)?

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

`YES` или `NO`.""",
["abca", "abcd"], diff=25)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k == 0 else ('abc' if k < 6 else 'abcdefghijklmnopqrstuvwxyz')
        h = ''.join(rnd.choice(al) for _ in range(max(1, n // 2)))
        s = list(h + rnd.choice(['', 'a']) + h[::-1])
        if rnd.random() < 0.5:
            s.insert(rnd.randrange(len(s) + 1), rnd.choice(al))
        if rnd.random() < 0.3:
            s[rnd.randrange(len(s))] = rnd.choice(al)
        return ''.join(s) + '\n'

    def sol(inp):
        s = inp.split()[0]

        def pal(i, j):
            while i < j:
                if s[i] != s[j]:
                    return False
                i += 1
                j -= 1
            return True
        i, j = 0, len(s) - 1
        while i < j:
            if s[i] != s[j]:
                return 'YES' if pal(i + 1, j) or pal(i, j - 1) else 'NO'
            i += 1
            j -= 1
        return 'YES'

    def brute(inp):
        s = inp.split()[0]
        if s == s[::-1]:
            return 'YES'
        for i in range(len(s)):
            t = s[:i] + s[i + 1:]
            if t == t[::-1]:
                return 'YES'
        return 'NO'
    return gen, sol, brute


@task('pal_longest_sub', 'Самый длинный палиндром',
"""Нурлан ищет в слове самую длинную подстроку (подряд идущие буквы), которая является палиндромом.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Длина самой длинной подстроки-палиндрома.""",
["babad", "aaaa"], diff=45)
def _():
    def gen(n, rnd, k):
        al = 'ab' if (k == 0 or k < 7) else 'abc'
        s = ''.join(rnd.choice(al) for _ in range(n))
        if k >= 5:
            h = ''.join(rnd.choice(al) for _ in range(n // 3))
            p = rnd.randrange(0, n - len(h) * 2 + 1) if n - len(h) * 2 > 0 else 0
            s = (s[:p] + h + h[::-1] + s[p + 2 * len(h):])[:n]
        return s + '\n'

    def sol(inp):
        s = inp.split()[0]
        t = '^#' + '#'.join(s) + '#$'
        n = len(t)
        p = [0] * n
        c = r = 0
        for i in range(1, n - 1):
            if i < r:
                p[i] = min(r - i, p[2 * c - i])
            while t[i + 1 + p[i]] == t[i - 1 - p[i]]:
                p[i] += 1
            if i + p[i] > r:
                c, r = i, i + p[i]
        return str(max(p))

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        best = 0
        for i in range(n):
            for j in range(i, n):
                t = s[i:j + 1]
                if t == t[::-1] and len(t) > best:
                    best = len(t)
        return str(best)
    return gen, sol, brute


@task('pal_count_sub', 'Сколько палиндромов',
"""Зарина записала строку и хочет посчитать все её подстроки-палиндромы. Подстроки с разными позициями считаются разными, даже если они совпадают как слова.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Количество подстрок-палиндромов.""",
["aaa", "abc"], diff=45)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 8 else 'a'
        if k == 10:
            return 'a' * n + '\n'
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        t = '^#' + '#'.join(s) + '#$'
        n = len(t)
        p = [0] * n
        c = r = 0
        for i in range(1, n - 1):
            if i < r:
                p[i] = min(r - i, p[2 * c - i])
            while t[i + 1 + p[i]] == t[i - 1 - p[i]]:
                p[i] += 1
            if i + p[i] > r:
                c, r = i, i + p[i]
        return str(sum((x + 1) // 2 for x in p))

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        cnt = 0
        for i in range(n):
            for j in range(i, n):
                t = s[i:j + 1]
                if t == t[::-1]:
                    cnt += 1
        return str(cnt)
    return gen, sol, brute


@task('pal_min_insert', 'Достроить палиндром',
"""Эрлан может вставлять в слово буквы в любые места. Какое наименьшее число вставок превратит слово в палиндром?

## Вход

Одна строка из строчных латинских букв, длина от 1 до 1000.

## Выход

Наименьшее число вставок.""",
["ab", "mom"], sizes=QUAD, diff=40)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 5 else 'abcd'
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        r = s[::-1]
        n = len(s)
        prev = [0] * (n + 1)
        for i in range(1, n + 1):
            cur = [0] * (n + 1)
            a = s[i - 1]
            for j in range(1, n + 1):
                if a == r[j - 1]:
                    cur[j] = prev[j - 1] + 1
                else:
                    cur[j] = max(prev[j], cur[j - 1])
            prev = cur
        return str(n - prev[n])

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        best = 0
        for m in range(1 << n):
            t = [s[i] for i in range(n) if m >> i & 1]
            if t == t[::-1] and len(t) > best:
                best = len(t)
        return str(n - best)
    return gen, sol, brute


@task('pal_prepend', 'Короткий палиндром спереди',
"""Асел может дописывать буквы только в начало слова. Найдите самый короткий палиндром, который можно так получить.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Самый короткий палиндром, который начинается с дописанных букв и заканчивается исходным словом.""",
["aacecaaa", "abcd"], diff=50)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 6 else 'abc'
        h = ''.join(rnd.choice(al) for _ in range(n // 2))
        s = h + rnd.choice(['', 'a']) + h[::-1]
        s = s[:max(1, n - rnd.randint(0, min(3, n - 1)))] if k else s
        tail = ''.join(rnd.choice(al) for _ in range(max(0, n - len(s))))
        s = (s + tail)[:n] or 'a'
        return s + '\n'

    def sol(inp):
        s = inp.split()[0]
        r = s[::-1]
        t = s + '#' + r
        pi = [0] * len(t)
        for i in range(1, len(t)):
            j = pi[i - 1]
            while j and t[i] != t[j]:
                j = pi[j - 1]
            if t[i] == t[j]:
                j += 1
            pi[i] = j
        L = pi[-1]
        return s[L:][::-1] + s

    def brute(inp):
        s = inp.split()[0]
        r = s[::-1]
        for t in range(len(s) + 1):
            c = r[:t] + s
            if c == c[::-1]:
                return c
    return gen, sol, brute


@task('pal_subseq', 'Палиндром из букв',
"""Чолпон вычёркивает из слова некоторые буквы (возможно, ни одной), а оставшиеся не переставляет. Какой наибольшей длины палиндром можно получить?

## Вход

Одна строка из строчных латинских букв, длина от 1 до 1000.

## Выход

Наибольшая длина палиндрома.""",
["bbbab", "abc"], sizes=QUAD, diff=40)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 4 else 'abcde'
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        n = len(s)
        dp = [[0] * n for _ in range(n)]
        for i in range(n - 1, -1, -1):
            dp[i][i] = 1
            for j in range(i + 1, n):
                if s[i] == s[j]:
                    dp[i][j] = dp[i + 1][j - 1] + 2 if i + 1 <= j - 1 else 2
                else:
                    dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
        return str(dp[0][n - 1])

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        best = 0
        for m in range(1, 1 << n):
            t = [s[i] for i in range(n) if m >> i & 1]
            if t == t[::-1] and len(t) > best:
                best = len(t)
        return str(best)
    return gen, sol, brute


@task('pal_cuts', 'Разрезать на палиндромы',
"""Мээрим режет слово на несколько частей так, чтобы каждая часть была палиндромом. Сколько разрезов нужно минимум?

## Вход

Одна строка из строчных латинских букв, длина от 1 до 1000.

## Выход

Наименьшее число разрезов (если слово уже палиндром, ответ 0).""",
["aab", "racecar"], sizes=QUAD, diff=50)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 4 else 'abc'
        if k > 7:
            h = ''.join(rnd.choice('ab') for _ in range(rnd.randint(1, 3)))
            s = ''
            while len(s) < n:
                s += h + h[::-1] if rnd.random() < 0.5 else h
            return s[:n] + '\n'
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        n = len(s)
        pal = [[False] * n for _ in range(n)]
        for i in range(n - 1, -1, -1):
            for j in range(i, n):
                if s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1]):
                    pal[i][j] = True
        dp = [0] * n
        for j in range(n):
            if pal[0][j]:
                dp[j] = 0
            else:
                dp[j] = min(dp[i - 1] + 1 for i in range(1, j + 1) if pal[i][j])
        return str(dp[n - 1])

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        best = n
        for m in range(1 << (n - 1)):
            parts = []
            st = 0
            for i in range(n - 1):
                if m >> i & 1:
                    parts.append(s[st:i + 1])
                    st = i + 1
            parts.append(s[st:])
            if all(p == p[::-1] for p in parts):
                best = min(best, len(parts) - 1)
        return str(best)
    return gen, sol, brute


@task('pal_distinct', 'Разные палиндромы',
"""Тилек выписал все подстроки-палиндромы слова. Сколько среди них различных слов?

## Вход

Одна строка из строчных латинских букв, длина от 1 до 100000.

## Выход

Количество различных подстрок-палиндромов.""",
["aaa", "abacaba"], sizes=MID, diff=70, tl=2.0)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 8 else 'abc'
        if k == 10:
            return ''.join(rnd.choice('ab') for _ in range(n // 2)) * 2 + '\n'
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        ln = [-1, 0]
        link = [0, 0]
        nxt = [{}, {}]
        last = 1
        for i, c in enumerate(s):
            cur = last
            while True:
                l = ln[cur]
                if i - l - 1 >= 0 and s[i - l - 1] == c:
                    break
                cur = link[cur]
            if c in nxt[cur]:
                last = nxt[cur][c]
                continue
            ln.append(ln[cur] + 2)
            nxt.append({})
            new = len(ln) - 1
            if ln[new] == 1:
                link.append(1)
            else:
                p = link[cur]
                while True:
                    l = ln[p]
                    if i - l - 1 >= 0 and s[i - l - 1] == c:
                        break
                    p = link[p]
                link.append(nxt[p][c])
            nxt[cur][c] = new
            last = new
        return str(len(ln) - 2)

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        st = set()
        for i in range(n):
            for j in range(i, n):
                t = s[i:j + 1]
                if t == t[::-1]:
                    st.add(t)
        return str(len(st))
    return gen, sol, brute


@task('pal_from_letters', 'Палиндром из набора',
"""У Алтынай есть набор букв-карточек (заглавные и строчные буквы различаются). Она выкладывает из некоторых карточек палиндром, расставляя их как угодно. Какой наибольшей длины палиндром можно выложить?

## Вход

Одна строка из латинских букв, длина от 1 до 200000.

## Выход

Наибольшая длина палиндрома.""",
["abccccdd", "Aa"], diff=15)
def _():
    def gen(n, rnd, k):
        al = 'aAbB' if k < 5 else 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        from collections import Counter
        c = Counter(s)
        ans = sum(v // 2 * 2 for v in c.values())
        if any(v % 2 for v in c.values()):
            ans += 1
        return str(ans)

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        best = 0
        for m in range(1, 1 << n):
            cnt = {}
            for i in range(n):
                if m >> i & 1:
                    cnt[s[i]] = cnt.get(s[i], 0) + 1
            if sum(v % 2 for v in cnt.values()) <= 1:
                best = max(best, bin(m).count('1'))
        return str(best)
    return gen, sol, brute


@task('pal_next', 'Следующее зеркальное число',
"""Билет в Ошском театре называется счастливым, если его номер читается одинаково слева направо и справа налево. Дан номер билета. Найдите наименьший счастливый номер, строго больший данного (длина может увеличиться).

## Вход

Одна строка: число без ведущих нулей, от 1 до 100000 цифр.

## Выход

Наименьшее палиндромное число, большее данного.""",
["123", "99"], diff=55)
def _():
    def gen(n, rnd, k):
        if k == 0:
            n = min(n, 6)
        r = rnd.random()
        if r < 0.15:
            return '9' * n + '\n'
        s = rnd.choice('123456789') + ''.join(rnd.choice('0123456789' if r < 0.6 else '9') for _ in range(n - 1))
        if r > 0.8 and n > 1:
            h = s[:n // 2]
            s = h + (s[n // 2] if n % 2 else '') + h[::-1]
        return s + '\n'

    def sol(inp):
        x = inp.split()[0]
        n = len(x)
        if all(c == '9' for c in x):
            return '1' + '0' * (n - 1) + '1'
        h = (n + 1) // 2
        left = x[:h]

        def mk(l):
            return l + l[:n // 2][::-1]
        c = mk(left)
        if c > x:
            return c
        d = list(left)
        i = len(d) - 1
        while d[i] == '9':
            d[i] = '0'
            i -= 1
        d[i] = chr(ord(d[i]) + 1)
        return mk(''.join(d))

    def brute(inp):
        x = int(inp.split()[0]) + 1
        while True:
            t = str(x)
            if t == t[::-1]:
                return t
            x += 1
    return gen, sol, brute


@task('pal_swaps', 'Перестановка в палиндром',
"""Из букв слова можно составить палиндром. За один ход Нурсултан меняет местами две соседние буквы. За какое наименьшее число ходов слово станет палиндромом?

## Вход

Одна строка из строчных латинских букв, длина от 1 до 2000. Гарантируется, что палиндром получить можно.

## Выход

Наименьшее число ходов.""",
["aabb", "letelt"], sizes=[3, 8, 15, 50, 100, 300, 800, 1500, 2000, 2000], diff=60)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k == 0 else ('abc' if k < 6 else 'abcdefghij')
        h = [rnd.choice(al) for _ in range(n // 2)]
        s = h + h[:]
        if n % 2:
            s.append(rnd.choice(al))
        rnd.shuffle(s)
        return ''.join(s) + '\n'

    def sol(inp):
        s = list(inp.split()[0])
        n = len(s)
        ans = 0
        l, r = 0, n - 1
        while l < r:
            k = r
            while k > l and s[k] != s[l]:
                k -= 1
            if k == l:
                s[l], s[l + 1] = s[l + 1], s[l]
                ans += 1
                continue
            for j in range(k, r):
                s[j], s[j + 1] = s[j + 1], s[j]
                ans += 1
            l += 1
            r -= 1
        return str(ans)

    def brute(inp):
        s = inp.split()[0]
        from collections import deque
        d = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            if u == u[::-1]:
                return str(d[u])
            for i in range(len(u) - 1):
                v = u[:i] + u[i + 1] + u[i] + u[i + 2:]
                if v not in d:
                    d[v] = d[u] + 1
                    q.append(v)
    return gen, sol, brute


@task('pal_queries', 'Запросы о палиндромах',
"""Дана строка. Нужно отвечать на вопросы: является ли подстрока с позиции l по позицию r палиндромом.

## Вход

В первой строке записана строка из строчных латинских букв длиной от 1 до 100000. Во второй строке число запросов q (1 ≤ q ≤ 100000). В следующих q строках по два числа l и r (1 ≤ l ≤ r ≤ длины строки).

## Выход

Для каждого запроса `YES` или `NO` на отдельной строке.""",
["abacaba\n3\n1 7\n2 4\n3 5"], sizes=MID, diff=60, tl=2.0)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 8 else 'abc'
        s = ''
        while len(s) < n:
            h = ''.join(rnd.choice(al) for _ in range(rnd.randint(1, 4)))
            s += h + h[::-1] if rnd.random() < 0.6 else h
        s = s[:n]
        q = n if k else 5
        q = min(q, 100000)
        lines = [s, str(q)]
        for _ in range(q):
            if rnd.random() < 0.5:
                c = rnd.randrange(n)
                d = rnd.randint(0, min(c, n - 1 - c, 6))
                l, r = c - d, c + d
            else:
                l = rnd.randrange(n)
                r = rnd.randrange(l, n)
            lines.append('%d %d' % (l + 1, r + 1))
        return '\n'.join(lines) + '\n'

    def sol(inp):
        a = inp.split()
        s = a[0]
        q = int(a[1])
        t = '^#' + '#'.join(s) + '#$'
        n = len(t)
        p = [0] * n
        c = r = 0
        for i in range(1, n - 1):
            if i < r:
                p[i] = min(r - i, p[2 * c - i])
            while t[i + 1 + p[i]] == t[i - 1 - p[i]]:
                p[i] += 1
            if i + p[i] > r:
                c, r = i, i + p[i]
        out = []
        for i in range(q):
            l = int(a[2 + 2 * i]) - 1
            rr = int(a[3 + 2 * i]) - 1
            out.append('YES' if p[l + rr + 2] >= rr - l + 1 else 'NO')
        return '\n'.join(out)

    def brute(inp):
        a = inp.split()
        s = a[0]
        q = int(a[1])
        out = []
        for i in range(q):
            l = int(a[2 + 2 * i]) - 1
            r = int(a[3 + 2 * i])
            t = s[l:r]
            out.append('YES' if t == t[::-1] else 'NO')
        return '\n'.join(out)
    return gen, sol, brute
