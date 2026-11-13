from reg import task, LIN, MID, QUAD, SMALLQ

SAM_SRC = None


@task('aho_total', 'Словарь в тексте',
"""Редактор Каныбек проверяет текст на запрещённые слова. Дан текст и список слов. Посчитайте, сколько всего раз слова из списка встречаются в тексте. Вхождения могут пересекаться; каждое слово списка считается отдельно, даже если в списке есть одинаковые слова.

## Вход

В первой строке текст из строчных латинских букв, длина от 1 до 100000. Во второй строке число слов m (1 ≤ m ≤ 50000). Затем m строк со словами из строчных латинских букв. Суммарная длина слов не больше 100000.

## Выход

Общее число вхождений.""",
["abababa\n3\naba\nb\nzz"], sizes=MID, diff=75, tl=2.0)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 8 else 'abc'
        s = ''.join(rnd.choice(al) for _ in range(n))
        m = max(1, min(50000, n if k else 4))
        mx = max(1, min(6, 100000 // m))
        ws = [''.join(rnd.choice(al) for _ in range(rnd.randint(1, mx))) for _ in range(m)]
        return s + '\n' + str(m) + '\n' + '\n'.join(ws) + '\n'

    def sol(inp):
        a = inp.split()
        s = a[0]
        m = int(a[1])
        go = [{}]
        cnt = [0]
        for w in a[2:2 + m]:
            v = 0
            for c in w:
                if c not in go[v]:
                    go.append({})
                    cnt.append(0)
                    go[v][c] = len(go) - 1
                v = go[v][c]
            cnt[v] += 1
        fail = [0] * len(go)
        order = []
        q = list(go[0].values())
        order = q[:]
        i = 0
        while i < len(q):
            u = q[i]
            i += 1
            for c, v in go[u].items():
                f = fail[u]
                while f and c not in go[f]:
                    f = fail[f]
                fail[v] = go[f][c] if c in go[f] and go[f][c] != v else 0
                q.append(v)
        for u in q:
            cnt[u] += cnt[fail[u]]
        v = 0
        res = 0
        for c in s:
            while v and c not in go[v]:
                v = fail[v]
            v = go[v].get(c, 0)
            res += cnt[v]
        return str(res)

    def brute(inp):
        a = inp.split()
        s = a[0]
        m = int(a[1])
        res = 0
        for w in a[2:2 + m]:
            for i in range(len(s) - len(w) + 1):
                if s[i:i + len(w)] == w:
                    res += 1
        return str(res)
    return gen, sol, brute


@task('kmp_find', 'Поиск слова',
"""Найдите все места, где слово встречается в тексте.

## Вход

Первая строка — текст, вторая — слово. Обе из строчных латинских букв, длина каждой от 1 до 200000.

## Выход

В первой строке количество вхождений (они могут пересекаться). Если оно больше нуля, во второй строке позиции начал вхождений по возрастанию (нумерация с 1).""",
["abababa\naba", "abc\nd"], diff=25)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 9 else 'a'
        s = ''.join(rnd.choice(al) for _ in range(n))
        m = rnd.randint(1, max(1, min(n, 3 if k < 5 else 8)))
        p = ''.join(rnd.choice(al) for _ in range(m))
        if k == 10:
            p = 'a' * rnd.randint(1, 5)
        return s + '\n' + p + '\n'

    def sol(inp):
        s, p = inp.split()[:2]
        t = p + '#' + s
        pi = [0] * len(t)
        res = []
        m = len(p)
        for i in range(1, len(t)):
            j = pi[i - 1]
            while j and t[i] != t[j]:
                j = pi[j - 1]
            if t[i] == t[j]:
                j += 1
            pi[i] = j
            if j == m:
                res.append(i - 2 * m + 1)
        if not res:
            return '0'
        return str(len(res)) + '\n' + ' '.join(map(str, res))

    def brute(inp):
        s, p = inp.split()[:2]
        res = [i + 1 for i in range(len(s) - len(p) + 1) if s[i:i + len(p)] == p]
        if not res:
            return '0'
        return str(len(res)) + '\n' + ' '.join(map(str, res))
    return gen, sol, brute


@task('prefix_func', 'Префикс-функция',
"""Для каждой позиции i слова найдите длину самого длинного собственного префикса подстроки s[1..i], который одновременно является её суффиксом. Собственный префикс не равен всей подстроке; если подходящего нет, ответ 0.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

n чисел через пробел: ответы для i = 1, 2, …, n.""",
["abacaba", "aaaa"], diff=30)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 8 else 'abc'
        if k == 10:
            return 'a' * (n - 1) + 'b\n'
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        pi = [0] * len(s)
        for i in range(1, len(s)):
            j = pi[i - 1]
            while j and s[i] != s[j]:
                j = pi[j - 1]
            if s[i] == s[j]:
                j += 1
            pi[i] = j
        return ' '.join(map(str, pi))

    def brute(inp):
        s = inp.split()[0]
        res = []
        for i in range(1, len(s) + 1):
            t = s[:i]
            best = 0
            for l in range(1, i):
                if t[:l] == t[i - l:]:
                    best = l
            res.append(best)
        return ' '.join(map(str, res))
    return gen, sol, brute


@task('z_func', 'Z-функция',
"""Для каждой позиции i слова найдите длину наибольшего общего начала слова и его суффикса, который начинается в позиции i. Для i = 1 ответом считается длина всего слова.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

n чисел через пробел.""",
["aaabaab", "abc"], diff=30)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 8 else 'abc'
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        n = len(s)
        z = [0] * n
        z[0] = n
        l = r = 0
        for i in range(1, n):
            if i < r:
                z[i] = min(r - i, z[i - l])
            while i + z[i] < n and s[z[i]] == s[i + z[i]]:
                z[i] += 1
            if i + z[i] > r:
                l, r = i, i + z[i]
        return ' '.join(map(str, z))

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        res = []
        for i in range(n):
            j = 0
            while i + j < n and s[j] == s[i + j]:
                j += 1
            res.append(j)
        return ' '.join(map(str, res))
    return gen, sol, brute


@task('smallest_period', 'Период слова',
"""Периодом слова называется число p такое, что любая буква совпадает с буквой на p позиций правее неё (если такая есть). Наименьший период может не делить длину слова. Найдите наименьший период.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Наименьший период.""",
["abcabca", "abcd"], diff=25)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 8 else 'abc'
        p = rnd.randint(1, max(1, min(n, 4 if k < 6 else n // 3 + 1)))
        base = ''.join(rnd.choice(al) for _ in range(p))
        s = (base * (n // p + 1))[:n]
        if rnd.random() < 0.3:
            s = s[:-1] + rnd.choice(al)
        return s + '\n'

    def sol(inp):
        s = inp.split()[0]
        pi = [0] * len(s)
        for i in range(1, len(s)):
            j = pi[i - 1]
            while j and s[i] != s[j]:
                j = pi[j - 1]
            if s[i] == s[j]:
                j += 1
            pi[i] = j
        return str(len(s) - pi[-1])

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        for p in range(1, n + 1):
            if all(s[i] == s[i + p] for i in range(n - p)):
                return str(p)
    return gen, sol, brute


@task('repeat_roots', 'Повторы целиком',
"""Сколькими способами слово можно получить, записав подряд несколько одинаковых копий (хотя бы две) какого-то слова? Способы различаются длиной повторяющегося слова.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Количество способов (0, если слово не разбивается на равные копии).""",
["abababab", "abcabc", "abcd"], diff=30)
def _():
    def gen(n, rnd, k):
        al = 'ab'
        divs = [d for d in range(1, n + 1) if n % d == 0]
        d = rnd.choice(divs)
        base = ''.join(rnd.choice(al) for _ in range(d))
        s = base * (n // d)
        if k > 5 and n > 1 and rnd.random() < 0.3:
            h = ''.join(rnd.choice(al) for _ in range(max(1, n // 12)))
            s = (h * (n // len(h) + 1))[:n]
            if n % len(h):
                s = s[:-1] + 'b'
        return s + '\n'

    def sol(inp):
        s = inp.split()[0]
        n = len(s)
        pi = [0] * n
        for i in range(1, n):
            j = pi[i - 1]
            while j and s[i] != s[j]:
                j = pi[j - 1]
            if s[i] == s[j]:
                j += 1
            pi[i] = j
        p = n - pi[-1]
        if n % p:
            return '0'
        q = n // p
        return str(sum(1 for d in range(2, q + 1) if q % d == 0))

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        return str(sum(1 for d in range(1, n) if n % d == 0 and s[:d] * (n // d) == s))
    return gen, sol, brute


@task('borders', 'Границы слова',
"""Границей слова называется непустое слово, которое является одновременно его началом и концом, но не совпадает со всем словом. Выведите длины всех границ.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

В первой строке число границ. Если оно больше нуля, во второй строке длины границ по возрастанию.""",
["abacaba", "abc"], diff=35)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 8 else 'abc'
        if k > 5:
            h = ''.join(rnd.choice(al) for _ in range(max(1, n // 6)))
            mid = ''.join(rnd.choice(al) for _ in range(max(0, n - 2 * len(h))))
            return (h + mid + h)[:max(n, 1)] + '\n'
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        pi = [0] * len(s)
        for i in range(1, len(s)):
            j = pi[i - 1]
            while j and s[i] != s[j]:
                j = pi[j - 1]
            if s[i] == s[j]:
                j += 1
            pi[i] = j
        res = []
        j = pi[-1]
        while j:
            res.append(j)
            j = pi[j - 1]
        res.reverse()
        if not res:
            return '0'
        return str(len(res)) + '\n' + ' '.join(map(str, res))

    def brute(inp):
        s = inp.split()[0]
        res = [l for l in range(1, len(s)) if s[:l] == s[len(s) - l:]]
        if not res:
            return '0'
        return str(len(res)) + '\n' + ' '.join(map(str, res))
    return gen, sol, brute


@task('z_sum', 'Сходство с суффиксами',
"""Сходством слова с его суффиксом называется длина их наибольшего общего начала. Найдите сумму сходств слова со всеми его суффиксами (включая само слово).

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Сумма сходств.""",
["ababa", "abc"], diff=40)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 9 else 'a'
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        n = len(s)
        z = [0] * n
        z[0] = n
        l = r = 0
        for i in range(1, n):
            if i < r:
                z[i] = min(r - i, z[i - l])
            while i + z[i] < n and s[z[i]] == s[i + z[i]]:
                z[i] += 1
            if i + z[i] > r:
                l, r = i, i + z[i]
        return str(sum(z))

    def brute(inp):
        s = inp.split()[0]
        tot = 0
        for i in range(len(s)):
            j = 0
            while i + j < len(s) and s[j] == s[i + j]:
                j += 1
            tot += j
        return str(tot)
    return gen, sol, brute


@task('shift_check', 'Сдвиг слова',
"""Циклический сдвиг влево на 1 переносит первую букву слова в конец. Даны слова s и t одной длины. За какое наименьшее число таких сдвигов s превращается в t?

## Вход

Две строки из строчных латинских букв одинаковой длины от 1 до 200000.

## Выход

Наименьшее число сдвигов (от 0 до n − 1) или `-1`, если получить t нельзя.""",
["kalam\nalamk", "abc\nacb"], diff=30)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 8 else 'abc'
        s = ''.join(rnd.choice(al) for _ in range(n))
        sh = rnd.randrange(n)
        t = s[sh:] + s[:sh]
        if rnd.random() < 0.3:
            t = list(t)
            t[rnd.randrange(n)] = rnd.choice(al)
            t = ''.join(t)
        return s + '\n' + t + '\n'

    def sol(inp):
        s, t = inp.split()[:2]
        n = len(s)
        w = t + '#' + s + s
        pi = [0] * len(w)
        for i in range(1, len(w)):
            j = pi[i - 1]
            while j and w[i] != w[j]:
                j = pi[j - 1]
            if w[i] == w[j]:
                j += 1
            pi[i] = j
            if j == n:
                st = i - 2 * n
                if st < n:
                    return str(st)
        return '-1'

    def brute(inp):
        s, t = inp.split()[:2]
        for k in range(len(s)):
            if s[k:] + s[:k] == t:
                return str(k)
        return '-1'
    return gen, sol, brute


@task('min_rotation', 'Наименьший сдвиг',
"""Из всех циклических сдвигов слова выберите лексикографически наименьший.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Наименьший циклический сдвиг.""",
["bca", "abab"], diff=45)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 9 else 'a'
        if k > 5:
            p = max(1, n // rnd.randint(1, 4))
            base = ''.join(rnd.choice(al) for _ in range(p))
            s = (base * (n // p + 1))[:n]
            return s + '\n'
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        n = len(s)
        d = s + s
        i, j, k = 0, 1, 0
        while i < n and j < n and k < n:
            a, b = d[i + k], d[j + k]
            if a == b:
                k += 1
                continue
            if a > b:
                i += k + 1
            else:
                j += k + 1
            if i == j:
                j += 1
            k = 0
        st = min(i, j)
        return d[st:st + n]

    def brute(inp):
        s = inp.split()[0]
        return min(s[i:] + s[:i] for i in range(len(s)))
    return gen, sol, brute


@task('distinct_rotations', 'Разные сдвиги',
"""Сколько различных слов получается из данного слова всеми циклическими сдвигами (включая нулевой)?

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Количество различных слов.""",
["abab", "abc", "aaaa"], diff=30)
def _():
    def gen(n, rnd, k):
        divs = [d for d in range(1, n + 1) if n % d == 0]
        d = rnd.choice(divs)
        base = ''.join(rnd.choice('ab') for _ in range(d))
        s = base * (n // d)
        if rnd.random() < 0.3 and n > 1:
            s = s[:-1] + rnd.choice('ab')
        return s + '\n'

    def sol(inp):
        s = inp.split()[0]
        n = len(s)
        pi = [0] * n
        for i in range(1, n):
            j = pi[i - 1]
            while j and s[i] != s[j]:
                j = pi[j - 1]
            if s[i] == s[j]:
                j += 1
            pi[i] = j
        p = n - pi[-1]
        return str(p if n % p == 0 else n)

    def brute(inp):
        s = inp.split()[0]
        return str(len(set(s[i:] + s[:i] for i in range(len(s)))))
    return gen, sol, brute


@task('overlap_count', 'Вхождения и непересекающиеся',
"""В тексте ищут слово. Сколько всего вхождений слова в текст (вхождения могут пересекаться)? А сколько вхождений можно выбрать так, чтобы никакие два не пересекались?

## Вход

Первая строка — текст, вторая — слово. Обе из строчных латинских букв, длина каждой от 1 до 200000.

## Выход

Два числа через пробел: все вхождения и наибольшее число непересекающихся.""",
["aaaaa\naa", "abcabc\nabc"], diff=25)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 9 else 'a'
        s = ''.join(rnd.choice(al) for _ in range(n))
        m = rnd.randint(1, max(1, min(n, 3 if k < 5 else 6)))
        return s + '\n' + ''.join(rnd.choice(al) for _ in range(m)) + '\n'

    def sol(inp):
        s, p = inp.split()[:2]
        m = len(p)
        t = p + '#' + s
        pi = [0] * len(t)
        tot = 0
        non = 0
        last = -1
        for i in range(1, len(t)):
            j = pi[i - 1]
            while j and t[i] != t[j]:
                j = pi[j - 1]
            if t[i] == t[j]:
                j += 1
            pi[i] = j
            if j == m:
                tot += 1
                st = i - 2 * m
                if st > last:
                    non += 1
                    last = st + m - 1
        return '%d %d' % (tot, non)

    def brute(inp):
        s, p = inp.split()[:2]
        m = len(p)
        pos = [i for i in range(len(s) - m + 1) if s[i:i + m] == p]
        non = 0
        nxt = 0
        for i in pos:
            if i >= nxt:
                non += 1
                nxt = i + m
        return '%d %d' % (len(pos), non)
    return gen, sol, brute


@task('wildcard_star', 'Шаблон со звёздочкой',
"""Шаблон состоит из букв и двух особых знаков: `?` заменяет ровно одну любую букву, `*` заменяет любую последовательность букв (в том числе пустую). Подходит ли весь текст под шаблон?

## Вход

В первой строке текст из строчных латинских букв, длина от 1 до 1000. Во второй строке шаблон из строчных букв и знаков `?` и `*`, длина от 1 до 1000.

## Выход

`YES` или `NO`.""",
["manas\nm*s", "manas\n?a?a"], sizes=QUAD, diff=45)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 6 else 'abc'
        s = ''.join(rnd.choice(al) for _ in range(n))
        m = rnd.randint(1, max(1, n // 2 + 1))
        if rnd.random() < 0.6:
            p = []
            for c in s:
                r = rnd.random()
                if r < 0.2:
                    p.append('*')
                elif r < 0.4:
                    p.append('?')
                elif r < 0.8:
                    p.append(c)
            p = ''.join(p) or '*'
            p = p.replace('**', '*')
        else:
            p = ''.join(rnd.choice(al + '??*') for _ in range(m))
        return s + '\n' + p + '\n'

    def sol(inp):
        s, p = inp.split()[:2]
        n, m = len(s), len(p)
        dp = [False] * (n + 1)
        dp[0] = True
        for j in range(1, m + 1):
            c = p[j - 1]
            new = [False] * (n + 1)
            if c == '*':
                new[0] = dp[0]
                for i in range(1, n + 1):
                    new[i] = dp[i] or new[i - 1]
            else:
                for i in range(1, n + 1):
                    if dp[i - 1] and (c == '?' or c == s[i - 1]):
                        new[i] = True
            dp = new
        return 'YES' if dp[n] else 'NO'

    def brute(inp):
        s, p = inp.split()[:2]
        import re
        rx = ''.join('.*' if c == '*' else '.' if c == '?' else c for c in p)
        return 'YES' if re.fullmatch(rx, s) else 'NO'
    return gen, sol, brute


@task('wildcard_count', 'Шаблон с вопросами',
"""В шаблоне знак `?` заменяет ровно одну любую букву. Сколько раз шаблон подходит к подстрокам текста (позиции считаются разными)?

## Вход

Первая строка — текст из строчных латинских букв, длина от 1 до 100000. Вторая строка — шаблон из строчных букв и знаков `?`, длина от 1 до 2000, не больше длины текста.

## Выход

Количество подходящих позиций.""",
["abcabc\na?c", "aaaa\n??"], sizes=MID, diff=45, tl=2.0)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 8 else 'abc'
        s = ''.join(rnd.choice(al) for _ in range(n))
        m = rnd.randint(1, max(1, min(n, 3 if k < 5 else 2000 if k > 8 else 200)))
        p = ''.join(rnd.choice(al + '??') for _ in range(m))
        return s + '\n' + p + '\n'

    def sol(inp):
        s, p = inp.split()[:2]
        n, m = len(s), len(p)
        mask = {}
        for i, c in enumerate(s):
            mask[c] = mask.get(c, 0) | (1 << i)
        full = (1 << (n - m + 1)) - 1
        res = full
        for j, c in enumerate(p):
            if c != '?':
                res &= mask.get(c, 0) >> j
        return str(bin(res & full).count('1'))

    def brute(inp):
        s, p = inp.split()[:2]
        n, m = len(s), len(p)
        return str(sum(1 for i in range(n - m + 1) if all(p[j] == '?' or p[j] == s[i + j] for j in range(m))))
    return gen, sol, brute


@task('distinct_substrings', 'Разные подстроки',
"""Сколько различных непустых подстрок у слова?

## Вход

Одна строка из строчных латинских букв, длина от 1 до 100000.

## Выход

Количество различных подстрок.""",
["aab", "aaaa"], sizes=MID, diff=70, tl=2.0)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 8 else 'abcdefghijklmnopqrstuvwxyz'
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        nxt = [{}]
        link = [-1]
        ln = [0]
        last = 0
        for c in s:
            cur = len(ln)
            ln.append(ln[last] + 1)
            link.append(0)
            nxt.append({})
            p = last
            while p != -1 and c not in nxt[p]:
                nxt[p][c] = cur
                p = link[p]
            if p != -1:
                q = nxt[p][c]
                if ln[p] + 1 == ln[q]:
                    link[cur] = q
                else:
                    cl = len(ln)
                    ln.append(ln[p] + 1)
                    nxt.append(dict(nxt[q]))
                    link.append(link[q])
                    while p != -1 and nxt[p].get(c) == q:
                        nxt[p][c] = cl
                        p = link[p]
                    link[q] = link[cur] = cl
            last = cur
        return str(sum(ln[i] - ln[link[i]] for i in range(1, len(ln))))

    def brute(inp):
        s = inp.split()[0]
        return str(len(set(s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1))))
    return gen, sol, brute


@task('distinct_len_k', 'Разные подстроки длины k',
"""Сколько различных подстрок длины ровно k у слова?

## Вход

В первой строке число k. Во второй строке слово из строчных латинских букв, длина n (1 ≤ k ≤ n ≤ 100000).

## Выход

Количество различных подстрок длины k.""",
["2\nabcab", "1\naaaa"], sizes=MID, diff=60, tl=2.0)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 8 else 'abc'
        kk = rnd.randint(1, n) if k < 8 else rnd.choice([n // 2, 17, 5, n - 3, 1])
        kk = max(1, min(n, kk))
        return str(kk) + '\n' + ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        nxt = [{}]
        link = [-1]
        ln = [0]
        last = 0
        for c in s:
            cur = len(ln)
            ln.append(ln[last] + 1)
            link.append(0)
            nxt.append({})
            p = last
            while p != -1 and c not in nxt[p]:
                nxt[p][c] = cur
                p = link[p]
            if p != -1:
                q = nxt[p][c]
                if ln[p] + 1 == ln[q]:
                    link[cur] = q
                else:
                    cl = len(ln)
                    ln.append(ln[p] + 1)
                    nxt.append(dict(nxt[q]))
                    link.append(link[q])
                    while p != -1 and nxt[p].get(c) == q:
                        nxt[p][c] = cl
                        p = link[p]
                    link[q] = link[cur] = cl
            last = cur
        return str(sum(1 for i in range(1, len(ln)) if ln[link[i]] < k <= ln[i]))

    def brute(inp):
        a = inp.split()
        k = int(a[0])
        s = a[1]
        return str(len(set(s[i:i + k] for i in range(len(s) - k + 1))))
    return gen, sol, brute


@task('longest_duplicate', 'Самый длинный повтор',
"""Найдите самую длинную строку, которая встречается в слове как подстрока не менее двух раз. Вхождения могут пересекаться.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 100000.

## Выход

Длина самой длинной повторяющейся подстроки (0, если повторов нет).""",
["banana", "abc"], sizes=MID, diff=65, tl=2.0)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 6 else 'abcdefghijklmnopqrstuvwxyz'
        s = ''.join(rnd.choice(al) for _ in range(n))
        if k > 6 and n > 20:
            L = n // 5
            i = rnd.randrange(n - L)
            j = rnd.randrange(n - L)
            if abs(i - j) > L:
                s = s[:j] + s[i:i + L] + s[j + L:]
        return s + '\n'

    def sol(inp):
        s = inp.split()[0]
        nxt = [{}]
        link = [-1]
        ln = [0]
        occ = [0]
        last = 0
        for c in s:
            cur = len(ln)
            ln.append(ln[last] + 1)
            link.append(0)
            nxt.append({})
            occ.append(1)
            p = last
            while p != -1 and c not in nxt[p]:
                nxt[p][c] = cur
                p = link[p]
            if p != -1:
                q = nxt[p][c]
                if ln[p] + 1 == ln[q]:
                    link[cur] = q
                else:
                    cl = len(ln)
                    ln.append(ln[p] + 1)
                    nxt.append(dict(nxt[q]))
                    link.append(link[q])
                    occ.append(0)
                    while p != -1 and nxt[p].get(c) == q:
                        nxt[p][c] = cl
                        p = link[p]
                    link[q] = link[cur] = cl
            last = cur
        order = sorted(range(1, len(ln)), key=lambda v: -ln[v])
        best = 0
        for v in order:
            if occ[v] >= 2 and ln[v] > best:
                best = ln[v]
            if link[v] > 0:
                occ[link[v]] += occ[v]
        return str(best)

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        for L in range(n - 1, 0, -1):
            seen = set()
            for i in range(n - L + 1):
                t = s[i:i + L]
                if t in seen:
                    return str(L)
                seen.add(t)
        return '0'
    return gen, sol, brute


@task('substr_equal_queries', 'Одинаковые куски',
"""Дано слово и запросы. В каждом запросе даны два куска слова (подстроки). Равны ли они как строки?

## Вход

В первой строке слово из строчных латинских букв, длина от 1 до 100000. Во второй строке число запросов q (1 ≤ q ≤ 100000). В каждой из следующих q строк четыре числа l1 r1 l2 r2 — границы двух подстрок (1 ≤ l ≤ r ≤ n, длины подстрок могут отличаться).

## Выход

Для каждого запроса `YES` или `NO`.""",
["abcabc\n2\n1 3 4 6\n1 2 2 3"], sizes=MID, diff=55, tl=2.0)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 8 else 'abc'
        p = rnd.randint(1, 4)
        base = ''.join(rnd.choice(al) for _ in range(p))
        s = list((base * (n // p + 1))[:n])
        for _ in range(max(1, n // 50)):
            s[rnd.randrange(n)] = rnd.choice(al)
        s = ''.join(s)
        q = n if k else 6
        q = min(q, 100000)
        out = [s, str(q)]
        for _ in range(q):
            l1 = rnd.randrange(n)
            r1 = rnd.randrange(l1, min(n, l1 + (4 if k < 7 else 30)))
            ln = r1 - l1 + 1
            if rnd.random() < 0.6:
                l2 = rnd.randrange(0, n - ln + 1)
                r2 = l2 + ln - 1
                if rnd.random() < 0.7 and l1 + p + ln <= n:
                    l2 = l1 + p * rnd.randint(1, max(1, (n - l1 - ln) // p))
                    l2 = min(l2, n - ln)
                    r2 = l2 + ln - 1
            else:
                l2 = rnd.randrange(n)
                r2 = rnd.randrange(l2, min(n, l2 + 5))
            out.append('%d %d %d %d' % (l1 + 1, r1 + 1, l2 + 1, r2 + 1))
        return '\n'.join(out) + '\n'

    def sol(inp):
        a = inp.split()
        s = a[0]
        q = int(a[1])
        M = (1 << 61) - 1
        B = 911382323 + 972663749
        n = len(s)
        h = [0] * (n + 1)
        pw = [1] * (n + 1)
        for i, c in enumerate(s):
            h[i + 1] = (h[i] * B + ord(c)) % M
            pw[i + 1] = pw[i] * B % M
        out = []
        for i in range(q):
            l1, r1, l2, r2 = (int(x) for x in a[2 + 4 * i:6 + 4 * i])
            if r1 - l1 != r2 - l2:
                out.append('NO')
                continue
            ln = r1 - l1 + 1
            x = (h[r1] - h[l1 - 1] * pw[ln]) % M
            y = (h[r2] - h[l2 - 1] * pw[ln]) % M
            out.append('YES' if x == y else 'NO')
        return '\n'.join(out)

    def brute(inp):
        a = inp.split()
        s = a[0]
        q = int(a[1])
        out = []
        for i in range(q):
            l1, r1, l2, r2 = (int(x) for x in a[2 + 4 * i:6 + 4 * i])
            out.append('YES' if s[l1 - 1:r1] == s[l2 - 1:r2] else 'NO')
        return '\n'.join(out)
    return gen, sol, brute
