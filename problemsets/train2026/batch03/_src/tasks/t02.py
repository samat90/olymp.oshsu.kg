from reg import task, LIN, MID, QUAD, SMALLQ


@task('anagram_yesno', 'Анаграммы',
"""Два слова называются анаграммами, если одно получается из другого перестановкой букв. Проверьте, являются ли слова Асылбека и Гулмиры анаграммами.

## Вход

Две строки из строчных латинских букв, длина каждой от 1 до 200000.

## Выход

`YES` или `NO`.""",
["listen\nsilent", "osh\nosha"], diff=5)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k == 0 else 'abcdefghijklmnopqrstuvwxyz'
        s = [rnd.choice(al) for _ in range(n)]
        t = s[:]
        rnd.shuffle(t)
        if rnd.random() < 0.5:
            t[rnd.randrange(n)] = rnd.choice(al)
        if rnd.random() < 0.1:
            t.append(rnd.choice(al))
        return ''.join(s) + '\n' + ''.join(t) + '\n'

    def sol(inp):
        a, b = inp.split()[:2]
        from collections import Counter
        return 'YES' if Counter(a) == Counter(b) else 'NO'

    def brute(inp):
        a, b = inp.split()[:2]
        return 'YES' if sorted(a) == sorted(b) else 'NO'
    return gen, sol, brute


@task('anagram_windows', 'Анаграммы в тексте',
"""Бакыт записал слово p и длинный текст s. Сколько подстрок текста длины |p| являются анаграммами слова p? Подстроки с разными позициями считаются разными.

## Вход

Первая строка — текст s, вторая — слово p. Обе из строчных латинских букв, 1 ≤ |p| ≤ |s| ≤ 200000.

## Выход

Количество подходящих подстрок.""",
["cbaebabacd\nabc", "aaaa\naa"], diff=30)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 8 else 'abc'
        m = rnd.randint(1, max(1, min(n, 6 if k == 0 else n // 3 + 1)))
        p = [rnd.choice(al) for _ in range(m)]
        s = [rnd.choice(al) for _ in range(n)]
        for _ in range(3):
            if n >= m:
                i = rnd.randrange(n - m + 1)
                q = p[:]
                rnd.shuffle(q)
                s[i:i + m] = q
        return ''.join(s) + '\n' + ''.join(p) + '\n'

    def sol(inp):
        s, p = inp.split()[:2]
        m = len(p)
        cnt = [0] * 26
        for c in p:
            cnt[ord(c) - 97] += 1
        for c in s[:m]:
            cnt[ord(c) - 97] -= 1
        bad = sum(1 for x in cnt if x)
        ans = 1 if bad == 0 else 0
        for i in range(m, len(s)):
            for c, d in ((s[i], -1), (s[i - m], 1)):
                j = ord(c) - 97
                if cnt[j]:
                    bad -= 1
                cnt[j] += d
                if cnt[j]:
                    bad += 1
            if bad == 0:
                ans += 1
        return str(ans)

    def brute(inp):
        s, p = inp.split()[:2]
        m = len(p)
        sp = sorted(p)
        return str(sum(1 for i in range(len(s) - m + 1) if sorted(s[i:i + m]) == sp))
    return gen, sol, brute


@task('anagram_groups', 'Группы анаграмм',
"""Список слов нужно разложить по группам: слова попадают в одну группу, если они анаграммы друг друга. Сколько получится групп? Одинаковые слова считаются анаграммами.

## Вход

В первой строке число слов n (1 ≤ n ≤ 50000). Во второй строке n слов из строчных латинских букв через пробел. Суммарная длина слов не больше 300000.

## Выход

Количество групп.""",
["6\nnaryn osh nayrn aso karakol sho"],
sizes=[3, 8, 15, 100, 1000, 5000, 10000, 20000, 50000, 50000], diff=15)
def _():
    def gen(n, rnd, k):
        al = 'abc' if k == 0 else 'abcdefg'
        ws = []
        for _ in range(n):
            ln = rnd.randint(1, 4 if k == 0 else 6)
            ws.append(''.join(rnd.choice(al) for _ in range(ln)))
        return str(n) + '\n' + ' '.join(ws) + '\n'

    def sol(inp):
        a = inp.split()
        n = int(a[0])
        return str(len(set(''.join(sorted(w)) for w in a[1:n + 1])))

    def brute(inp):
        a = inp.split()
        n = int(a[0])
        ws = a[1:n + 1]
        groups = []
        for w in ws:
            for g in groups:
                if sorted(g) == sorted(w):
                    break
            else:
                groups.append(w)
        return str(len(groups))
    return gen, sol, brute


@task('anagram_deletions', 'Стереть до анаграммы',
"""Жылдыз и Эмир записали по слову. Они стирают буквы (из любого слова, в любом месте), пока слова не станут анаграммами друг друга (пустые слова тоже считаются анаграммами). Какое наименьшее число букв придётся стереть?

## Вход

Две строки из строчных латинских букв, длина каждой от 1 до 200000.

## Выход

Наименьшее число стёртых букв.""",
["cde\nabc", "osh\nosh"], diff=10)
def _():
    def gen(n, rnd, k):
        if k == 0:
            n = min(n, 6)
        al = 'abc' if k == 0 else 'abcdefghij'
        s = ''.join(rnd.choice(al) for _ in range(n))
        m = max(1, n + rnd.randint(-2, 2)) if k == 0 else n
        t = ''.join(rnd.choice(al) for _ in range(m))
        return s + '\n' + t + '\n'

    def sol(inp):
        a, b = inp.split()[:2]
        from collections import Counter
        x, y = Counter(a), Counter(b)
        return str(sum(abs(x[c] - y[c]) for c in set(x) | set(y)))

    def brute(inp):
        a, b = inp.split()[:2]
        best = {}
        for m in range(1 << len(a)):
            key = ''.join(sorted(a[i] for i in range(len(a)) if m >> i & 1))
            best[key] = max(best.get(key, 0), len(key))
        keep = 0
        for m in range(1 << len(b)):
            key = ''.join(sorted(b[i] for i in range(len(b)) if m >> i & 1))
            if key in best:
                keep = max(keep, 2 * len(key))
        return str(len(a) + len(b) - keep)
    return gen, sol, brute


@task('first_unique', 'Первая уникальная буква',
"""В слове, которое написал Темирлан, нужно найти первую слева букву, которая встречается в слове ровно один раз.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Номер позиции этой буквы (нумерация с 1) или `-1`, если такой буквы нет.""",
["alamudun", "aabb"], diff=5)
def _():
    def gen(n, rnd, k):
        al = 'abc' if k == 0 else ('abcdefghijklmnopqrstuvwxyz' if k < 5 else 'abcdefghijklmnopqrstuvwxyz'[:rnd.randint(1, 26)])
        s = [rnd.choice(al) for _ in range(n)]
        if k > 6:
            h = ''.join(rnd.choice('abcdefghijklm') for _ in range(n // 2))
            s = list(h + h)
            if rnd.random() < 0.7 and s:
                s[rnd.randrange(len(s))] = 'z'
        return ''.join(s) + '\n'

    def sol(inp):
        s = inp.split()[0]
        from collections import Counter
        c = Counter(s)
        for i, ch in enumerate(s):
            if c[ch] == 1:
                return str(i + 1)
        return '-1'

    def brute(inp):
        s = inp.split()[0]
        for i in range(len(s)):
            if s.count(s[i]) == 1:
                return str(i + 1)
        return '-1'
    return gen, sol, brute


@task('top_word', 'Самое частое слово',
"""Каныкей разбирает объявления на базаре в Оше. Найдите слово, которое встречается чаще всех. Если таких несколько, выберите лексикографически наименьшее.

## Вход

В первой строке число слов n (1 ≤ n ≤ 100000). Во второй строке n слов из строчных латинских букв через пробел, длина слова не больше 10.

## Выход

Слово и сколько раз оно встречается, через пробел.""",
["5\nosh nary osh nary tokmok"], sizes=[3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000], diff=10)
def _():
    def gen(n, rnd, k):
        pool = ['osh', 'naryn', 'talas', 'batken', 'karakol', 'tokmok', 'kant', 'kara', 'balykchy', 'kerben']
        m = 3 if k == 0 else (4 + k)
        ws = []
        for _ in range(n):
            if rnd.random() < 0.7:
                ws.append(pool[rnd.randrange(min(m, 10))])
            else:
                ws.append(''.join(rnd.choice('abc') for _ in range(rnd.randint(1, 3))))
        return str(n) + '\n' + ' '.join(ws) + '\n'

    def sol(inp):
        a = inp.split()
        n = int(a[0])
        from collections import Counter
        c = Counter(a[1:n + 1])
        w = min(c, key=lambda x: (-c[x], x))
        return '%s %d' % (w, c[w])

    def brute(inp):
        a = inp.split()
        n = int(a[0])
        ws = a[1:n + 1]
        best = None
        for w in sorted(set(ws)):
            cnt = ws.count(w)
            if best is None or cnt > best[1]:
                best = (w, cnt)
        return '%s %d' % best
    return gen, sol, brute


@task('distinct_freq', 'Разные частоты',
"""Мирбек хочет, чтобы в его слове все буквы встречались разное число раз (буквы, которые не встречаются, не считаются). Он может стирать буквы. Какое наименьшее число букв нужно стереть?

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Наименьшее число стёртых букв.""",
["aaabbbcc", "abc"], diff=30)
def _():
    def gen(n, rnd, k):
        if k == 0:
            n = min(n, 11)
        al = 'abc' if k == 0 else 'abcdefghijklmnopqrstuvwxyz'
        w = [rnd.random() ** 2 for _ in al]
        return ''.join(rnd.choices(al, weights=w, k=n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        from collections import Counter
        cs = sorted(Counter(s).values(), reverse=True)
        used = set()
        ans = 0
        for c in cs:
            while c > 0 and c in used:
                c -= 1
                ans += 1
            if c > 0:
                used.add(c)
        return str(ans)

    def brute(inp):
        s = inp.split()[0]
        n = len(s)
        best = 0
        for m in range(1 << n):
            cnt = {}
            for i in range(n):
                if m >> i & 1:
                    cnt[s[i]] = cnt.get(s[i], 0) + 1
            v = list(cnt.values())
            if len(v) == len(set(v)):
                best = max(best, bin(m).count('1'))
        return str(n - best)
    return gen, sol, brute


@task('no_adjacent', 'Без соседей',
"""Дана строка. Можно ли переставить её буквы так, чтобы никакие две одинаковые буквы не стояли рядом?

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

`YES` или `NO`.""",
["aab", "aaab"], diff=20)
def _():
    def gen(n, rnd, k):
        if k == 0:
            n = min(n, 9)
        m = rnd.randint(1, 4 if k < 8 else 26)
        al = 'abcdefghijklmnopqrstuvwxyz'[:m]
        s = [rnd.choice(al) for _ in range(n)]
        if rnd.random() < 0.5:
            c = (n + 1) // 2 + rnd.randint(-1, 1)
            for i in range(max(0, min(n, c))):
                s[i] = 'z'
            rnd.shuffle(s)
        return ''.join(s) + '\n'

    def sol(inp):
        s = inp.split()[0]
        from collections import Counter
        return 'YES' if max(Counter(s).values()) <= (len(s) + 1) // 2 else 'NO'

    def brute(inp):
        s = inp.split()[0]
        from collections import Counter
        c = Counter(s)
        n = len(s)

        def go(prev, left):
            if left == 0:
                return True
            for ch in list(c):
                if ch != prev and c[ch] > 0:
                    c[ch] -= 1
                    ok = go(ch, left - 1)
                    c[ch] += 1
                    if ok:
                        return True
            return False
        return 'YES' if go('', n) else 'NO'
    return gen, sol, brute


@task('sort_by_freq', 'Сортировка по частоте',
"""Айгерим хочет переписать слово так, чтобы сначала шли самые частые буквы. Все копии одной буквы идут подряд. Буквы с одинаковой частотой упорядочите по алфавиту.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Получившаяся строка.""",
["tree", "alma"], diff=10)
def _():
    def gen(n, rnd, k):
        al = 'abc' if k == 0 else 'abcdefghijklmnopqrstuvwxyz'
        return ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        s = inp.split()[0]
        from collections import Counter
        c = Counter(s)
        return ''.join(ch * c[ch] for ch in sorted(c, key=lambda x: (-c[x], x)))

    def brute(inp):
        s = inp.split()[0]
        return ''.join(sorted(s, key=lambda ch: (-s.count(ch), ch)))
    return gen, sol, brute


@task('isomorphic', 'Замена букв',
"""У Данияра есть два слова одинаковой длины. Можно ли заменить буквы первого слова так, чтобы получилось второе, если разные буквы заменяются на разные, а одинаковые на одинаковые? (Буква может заменяться на саму себя.)

## Вход

Две строки из строчных латинских букв одинаковой длины от 1 до 200000.

## Выход

`YES` или `NO`.""",
["egg\nadd", "foo\nbar"], diff=10)
def _():
    def gen(n, rnd, k):
        al = 'abc' if k < 6 else 'abcdefghijklmnopqrstuvwxyz'
        s = [rnd.choice(al) for _ in range(n)]
        perm = list('abcdefghijklmnopqrstuvwxyz')
        rnd.shuffle(perm)
        t = [perm[ord(c) - 97] for c in s]
        if rnd.random() < 0.5:
            t[rnd.randrange(n)] = rnd.choice(al)
        return ''.join(s) + '\n' + ''.join(t) + '\n'

    def sol(inp):
        a, b = inp.split()[:2]

        def canon(x):
            d = {}
            return [d.setdefault(c, len(d)) for c in x]
        return 'YES' if canon(a) == canon(b) else 'NO'

    def brute(inp):
        a, b = inp.split()[:2]
        f, g = {}, {}
        for x, y in zip(a, b):
            if f.get(x, y) != y or g.get(y, x) != x:
                return 'NO'
            f[x] = y
            g[y] = x
        return 'YES'
    return gen, sol, brute


@task('ransom', 'Письмо из газеты',
"""Нургуль вырезает из газеты буквы, чтобы составить записку. Каждую вырезанную букву можно использовать один раз. Хватит ли букв газеты, чтобы составить записку?

## Вход

Первая строка — записка, вторая — газета. Обе из строчных латинских букв, длина каждой от 1 до 200000.

## Выход

`YES` или `NO`.""",
["aa\naab", "aaa\naab"], diff=5)
def _():
    def gen(n, rnd, k):
        al = 'abc' if k == 0 else 'abcdefghijklmnopqrstuvwxyz'
        g = [rnd.choice(al) for _ in range(n + rnd.randint(0, n // 5 + 2))]
        z = g[:]
        rnd.shuffle(z)
        note = z[:n]
        if rnd.random() < 0.5:
            note[rnd.randrange(n)] = rnd.choice(al)
        return ''.join(note) + '\n' + ''.join(g) + '\n'

    def sol(inp):
        a, b = inp.split()[:2]
        from collections import Counter
        x, y = Counter(a), Counter(b)
        return 'YES' if all(y[c] >= v for c, v in x.items()) else 'NO'

    def brute(inp):
        a, b = inp.split()[:2]
        pool = list(b)
        for c in a:
            if c in pool:
                pool.remove(c)
            else:
                return 'NO'
        return 'YES'
    return gen, sol, brute


@task('word_pattern', 'Шаблон слов',
"""Шаблон — строка из букв. Дана последовательность слов той же длины, что и шаблон. Подходит ли она под шаблон: одинаковым буквам шаблона соответствуют одинаковые слова, а разным буквам разные слова?

## Вход

В первой строке шаблон из строчных латинских букв, длина m от 1 до 50000. Во второй строке m слов из строчных латинских букв через пробел, длина каждого слова не больше 10.

## Выход

`YES` или `NO`.""",
["abba\nosh nary nary osh", "abba\nosh osh osh osh"],
sizes=[3, 8, 15, 100, 1000, 5000, 10000, 20000, 50000, 50000], diff=15)
def _():
    def gen(n, rnd, k):
        al = 'abc' if k < 6 else 'abcdefghijklmnopqrstuvwxyz'
        p = [rnd.choice(al) for _ in range(n)]
        names = {}
        for c in 'abcdefghijklmnopqrstuvwxyz':
            names[c] = ''.join(rnd.choice('xyz') for _ in range(6)) + c
        ws = [names[c] for c in p]
        if rnd.random() < 0.5:
            i = rnd.randrange(n)
            ws[i] = names[rnd.choice(al)]
        if rnd.random() < 0.2:
            j = rnd.randrange(n)
            ws[j] = 'q'
        return ''.join(p) + '\n' + ' '.join(ws) + '\n'

    def sol(inp):
        a = inp.split()
        p = a[0]
        ws = a[1:]
        if len(ws) != len(p):
            return 'NO'
        d1, d2 = {}, {}
        for c, w in zip(p, ws):
            if d1.setdefault(c, w) != w or d2.setdefault(w, c) != c:
                return 'NO'
        return 'YES'

    def brute(inp):
        a = inp.split()
        p = a[0]
        ws = a[1:]
        for i in range(len(p)):
            for j in range(len(p)):
                if (p[i] == p[j]) != (ws[i] == ws[j]):
                    return 'NO'
        return 'YES'
    return gen, sol, brute


@task('custom_order', 'Свой алфавит',
"""У Аселя собственный порядок букв: он задаётся строкой из различных букв. Нужно отсортировать буквы слова по этому порядку. Буквы, которых нет в порядке, ставятся в конец в обычном алфавитном порядке.

## Вход

В первой строке порядок (различные строчные латинские буквы, от 1 до 26). Во второй строке слово из строчных латинских букв, длина от 1 до 200000.

## Выход

Отсортированное слово.""",
["cba\nabcd", "zyx\nhello"], diff=10)
def _():
    def gen(n, rnd, k):
        letters = list('abcdefghijklmnopqrstuvwxyz')
        rnd.shuffle(letters)
        order = ''.join(letters[:rnd.randint(1, 26 if k else 5)])
        al = 'abcdef' if k == 0 else 'abcdefghijklmnopqrstuvwxyz'
        return order + '\n' + ''.join(rnd.choice(al) for _ in range(n)) + '\n'

    def sol(inp):
        o, s = inp.split()[:2]
        pos = {c: i for i, c in enumerate(o)}
        cnt = {}
        for c in s:
            cnt[c] = cnt.get(c, 0) + 1
        res = [c * cnt[c] for c in o if c in cnt]
        rest = sorted(c for c in cnt if c not in pos)
        res += [c * cnt[c] for c in rest]
        return ''.join(res)

    def brute(inp):
        o, s = inp.split()[:2]
        return ''.join(sorted(s, key=lambda c: (o.index(c) if c in o else 100, c)))
    return gen, sol, brute
