from reg import task, LIN, MID, QUAD, SMALLQ

BIG = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]


@task('roman_to_int', 'Римские числа',
"""Старинные часы на башне в Караколе показывают время римскими цифрами. Переведите числа в обычную запись.

Римские цифры: I = 1, V = 5, X = 10, L = 50, C = 100, D = 500, M = 1000. Обычно цифры записывают от большей к меньшей и складывают. Если меньшая цифра стоит перед большей (IV, IX, XL, XC, CD, CM), она вычитается.

## Вход

В первой строке число q (1 ≤ q ≤ 4000). В следующих q строках по одному правильному римскому числу от 1 до 3999.

## Выход

Для каждого числа его значение на отдельной строке.""",
["3\nIII\nLVIII\nMCMXCIV"], sizes=[3, 8, 15, 100, 400, 1000, 2000, 3000, 3999, 3999], diff=10)
def _():
    def gen(n, rnd, k):
        def rom(x):
            t = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
                 (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
            r = ''
            for v, s in t:
                while x >= v:
                    r += s
                    x -= v
            return r
        q = min(n, 3999)
        xs = rnd.sample(range(1, 4000), q)
        return str(q) + '\n' + '\n'.join(rom(x) for x in xs) + '\n'

    def sol(inp):
        a = inp.split()
        q = int(a[0])
        v = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        out = []
        for w in a[1:q + 1]:
            t = 0
            for i, c in enumerate(w):
                if i + 1 < len(w) and v[c] < v[w[i + 1]]:
                    t -= v[c]
                else:
                    t += v[c]
            out.append(str(t))
        return '\n'.join(out)

    def brute(inp):
        a = inp.split()
        q = int(a[0])
        out = []
        for w in a[1:q + 1]:
            t = 0
            for tok, val in (('CM', 900), ('CD', 400), ('XC', 90), ('XL', 40), ('IX', 9), ('IV', 4)):
                while tok in w:
                    w = w.replace(tok, '', 1)
                    t += val
            for ch, val in (('M', 1000), ('D', 500), ('C', 100), ('L', 50), ('X', 10), ('V', 5), ('I', 1)):
                t += w.count(ch) * val
            out.append(str(t))
        return '\n'.join(out)
    return gen, sol, brute


@task('int_to_roman', 'В римской записи',
"""Запишите числа римскими цифрами. Обозначения: I = 1, V = 5, X = 10, L = 50, C = 100, D = 500, M = 1000. Числа 4, 9, 40, 90, 400, 900 записываются вычитанием: IV, IX, XL, XC, CD, CM. Одна и та же цифра подряд пишется не более трёх раз.

## Вход

В первой строке число q (1 ≤ q ≤ 4000). В следующих q строках по числу от 1 до 3999.

## Выход

Для каждого числа его запись римскими цифрами на отдельной строке.""",
["3\n3\n58\n1994"], sizes=[3, 8, 15, 100, 400, 1000, 2000, 3000, 3999, 3999], diff=10)
def _():
    def gen(n, rnd, k):
        q = min(n, 3999)
        return str(q) + '\n' + '\n'.join(str(x) for x in rnd.sample(range(1, 4000), q)) + '\n'

    def sol(inp):
        a = inp.split()
        q = int(a[0])
        t = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
             (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
        out = []
        for x in a[1:q + 1]:
            x = int(x)
            r = []
            for v, s in t:
                while x >= v:
                    r.append(s)
                    x -= v
            out.append(''.join(r))
        return '\n'.join(out)

    def brute(inp):
        a = inp.split()
        q = int(a[0])
        th = ['', 'M', 'MM', 'MMM']
        h = ['', 'C', 'CC', 'CCC', 'CD', 'D', 'DC', 'DCC', 'DCCC', 'CM']
        te = ['', 'X', 'XX', 'XXX', 'XL', 'L', 'LX', 'LXX', 'LXXX', 'XC']
        o = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']
        out = []
        for x in a[1:q + 1]:
            x = int(x)
            out.append(th[x // 1000] + h[x // 100 % 10] + te[x // 10 % 10] + o[x % 10])
        return '\n'.join(out)
    return gen, sol, brute


@task('big_add', 'Сложение столбиком',
"""Сложите два очень больших неотрицательных числа.

## Вход

Две строки: десятичные записи чисел без ведущих нулей (число 0 записывается одной цифрой), длина каждой от 1 до 200000.

## Выход

Сумма чисел.""",
["99\n1", "123456789123456789\n987654321"], sizes=BIG, diff=10)
def _():
    def gen(n, rnd, k):
        def num(m):
            return rnd.choice('123456789') + ''.join(rnd.choice('0123456789') for _ in range(m - 1)) if m > 1 else rnd.choice('0123456789')
        if rnd.random() < 0.15:
            return '9' * n + '\n' + rnd.choice(['1', '9' * rnd.randint(1, n)]) + '\n'
        return num(n) + '\n' + num(rnd.randint(1, n)) + '\n'

    def sol(inp):
        a, b = inp.split()[:2]
        i, j = len(a) - 1, len(b) - 1
        c = 0
        res = []
        while i >= 0 or j >= 0 or c:
            t = c
            if i >= 0:
                t += ord(a[i]) - 48
                i -= 1
            if j >= 0:
                t += ord(b[j]) - 48
                j -= 1
            res.append(chr(48 + t % 10))
            c = t // 10
        return ''.join(reversed(res))

    def brute(inp):
        import sys
        if hasattr(sys, 'set_int_max_str_digits'):
            sys.set_int_max_str_digits(0)
        a, b = inp.split()[:2]
        return str(int(a) + int(b))
    return gen, sol, brute


@task('big_mul', 'Умножение больших чисел',
"""Перемножьте два больших неотрицательных числа.

## Вход

Две строки: десятичные записи чисел без ведущих нулей (число 0 записывается одной цифрой), длина каждой от 1 до 1000.

## Выход

Произведение чисел.""",
["12\n34", "999\n0"], sizes=[3, 8, 15, 50, 100, 300, 500, 800, 1000, 1000], diff=25)
def _():
    def gen(n, rnd, k):
        def num(m):
            return rnd.choice('123456789') + ''.join(rnd.choice('0123456789') for _ in range(m - 1)) if m > 1 else rnd.choice('0123456789')
        return num(n) + '\n' + num(max(1, n + rnd.randint(-2, 2))) + '\n'

    def sol(inp):
        a, b = inp.split()[:2]
        x = [int(c) for c in reversed(a)]
        y = [int(c) for c in reversed(b)]
        r = [0] * (len(x) + len(y) + 1)
        for i, u in enumerate(x):
            if u:
                for j, v in enumerate(y):
                    r[i + j] += u * v
        c = 0
        for i in range(len(r)):
            c += r[i]
            r[i] = c % 10
            c //= 10
        while len(r) > 1 and r[-1] == 0:
            r.pop()
        return ''.join(map(str, reversed(r)))

    def brute(inp):
        import sys
        if hasattr(sys, 'set_int_max_str_digits'):
            sys.set_int_max_str_digits(0)
        a, b = inp.split()[:2]
        return str(int(a) * int(b))
    return gen, sol, brute


@task('bin_add', 'Двоичное сложение',
"""Сложите два числа, записанных в двоичной системе.

## Вход

Две строки из `0` и `1` без ведущих нулей (число 0 записывается как `0`), длина каждой от 1 до 200000.

## Выход

Сумма в двоичной системе без ведущих нулей.""",
["11\n1", "1010\n1011"], sizes=BIG, diff=10)
def _():
    def gen(n, rnd, k):
        def num(m):
            return '1' + ''.join(rnd.choice('01') for _ in range(m - 1)) if m > 1 else rnd.choice('01')
        if rnd.random() < 0.2:
            return '1' * n + '\n' + '1' + '\n'
        return num(n) + '\n' + num(rnd.randint(1, n)) + '\n'

    def sol(inp):
        a, b = inp.split()[:2]
        i, j = len(a) - 1, len(b) - 1
        c = 0
        res = []
        while i >= 0 or j >= 0 or c:
            t = c
            if i >= 0:
                t += ord(a[i]) - 48
                i -= 1
            if j >= 0:
                t += ord(b[j]) - 48
                j -= 1
            res.append('1' if t & 1 else '0')
            c = t >> 1
        return ''.join(reversed(res))

    def brute(inp):
        a, b = inp.split()[:2]
        return bin(int(a, 2) + int(b, 2))[2:]
    return gen, sol, brute


@task('versions', 'Сравнение версий',
"""Номер версии записан числами через точки, например `1.02.10`. Версии сравниваются по частям слева направо как числа (ведущие нули не важны). Если в одной версии частей меньше, недостающие считаются нулями. Сравните две версии программы.

## Вход

Две строки — номера версий. Каждая состоит из чисел (от 0 до 10^9) через точки, не более 100000 частей, без пробелов.

## Выход

`-1`, если первая версия меньше, `1`, если больше, и `0`, если версии равны.""",
["1.01\n1.001", "1.0\n1.0.1"], sizes=MID, diff=15)
def _():
    def gen(n, rnd, k):
        def ver(m):
            return '.'.join(('0' * rnd.randint(0, 2)) + str(rnd.choice([0, 1, 2, 10, rnd.randint(0, 10 ** 9)]) if k > 5 else rnd.randint(0, 2)) for _ in range(m))
        m = max(1, n)
        a = ver(m)
        parts = a.split('.')
        r = rnd.random()
        if r < 0.3:
            b = a + '.0' * rnd.randint(0, 3)
        elif r < 0.6:
            b = '.'.join(parts[:-1] + [str(int(parts[-1]) + rnd.choice([-1, 1, 0]) if int(parts[-1]) > 0 else 1)])
        else:
            b = ver(max(1, m + rnd.randint(-2, 2)))
        return a + '\n' + b + '\n'

    def sol(inp):
        a, b = inp.split()[:2]
        x = [int(t) for t in a.split('.')]
        y = [int(t) for t in b.split('.')]
        for i in range(max(len(x), len(y))):
            u = x[i] if i < len(x) else 0
            v = y[i] if i < len(y) else 0
            if u != v:
                return '-1' if u < v else '1'
        return '0'

    def brute(inp):
        a, b = inp.split()[:2]
        x = [int(t) for t in a.split('.')]
        y = [int(t) for t in b.split('.')]
        m = max(len(x), len(y))
        x += [0] * (m - len(x))
        y += [0] * (m - len(y))
        return '-1' if x < y else '1' if x > y else '0'
    return gen, sol, brute


@task('simplify_path', 'Короткий путь',
"""Путь к файлу записан в стиле Linux. Упростите его: `.` означает текущую папку, `..` — родительскую (у корня родитель он сам), повторяющиеся `/` объединяются, в конце пути `/` не нужен (кроме корня). Имена, состоящие из точек, но не равные `.` и `..` (например `...`), — обычные имена папок.

## Вход

Одна строка, начинающаяся с `/`, из букв, цифр, `.` и `/`, длина от 1 до 200000.

## Выход

Упрощённый путь.""",
["/home//osh/./../nary/", "/../"], sizes=BIG, diff=20)
def _():
    def gen(n, rnd, k):
        parts = []
        L = 1
        while L < n:
            p = rnd.choice(['a', 'b', 'osh', '.', '..', '..', '...', 'x.y', '', 'c1'])
            parts.append(p)
            L += len(p) + 1
        s = '/' + '/'.join(parts)
        if rnd.random() < 0.5:
            s += '/'
        return s + '\n'

    def sol(inp):
        s = inp.split()[0]
        st = []
        for p in s.split('/'):
            if p == '' or p == '.':
                continue
            if p == '..':
                if st:
                    st.pop()
            else:
                st.append(p)
        return '/' + '/'.join(st)

    def brute(inp):
        s = inp.split()[0]
        while '//' in s:
            s = s.replace('//', '/')
        parts = s.strip('/').split('/') if s.strip('/') else []
        res = []
        i = 0
        while i < len(parts):
            if parts[i] == '.':
                pass
            elif parts[i] == '..':
                if res:
                    res = res[:-1]
            else:
                res = res + [parts[i]]
            i += 1
        return '/' + '/'.join(res)
    return gen, sol, brute


@task('zigzag', 'Зигзаг',
"""Слово записывают зигзагом по r строкам: первая буква в верхней строке, затем вниз до нижней строки, потом вверх по диагонали и так далее. Затем читают строки сверху вниз, слева направо. Например, слово `PAYPALISHIRING` при r = 3 записывается как

```
P   A   H   N
A P L S I I G
Y   I   R
```

и читается как `PAHNAPLSIIGYIR`. Выполните такое преобразование.

## Вход

В первой строке число r (1 ≤ r ≤ 1000). Во второй строке слово из латинских букв, длина от 1 до 200000.

## Выход

Прочитанное слово.""",
["3\nPAYPALISHIRING", "1\nABC"], sizes=BIG, diff=20)
def _():
    def gen(n, rnd, k):
        r = rnd.randint(1, 6 if k < 7 else 1000)
        return str(r) + '\n' + ''.join(rnd.choice('abcdefXYZ') for _ in range(n)) + '\n'

    def sol(inp):
        a = inp.split()
        r = int(a[0])
        s = a[1]
        if r == 1:
            return s
        rows = [[] for _ in range(r)]
        i, d = 0, 1
        for c in s:
            rows[i].append(c)
            if i == 0:
                d = 1
            elif i == r - 1:
                d = -1
            i += d
        return ''.join(''.join(x) for x in rows)

    def brute(inp):
        a = inp.split()
        r = int(a[0])
        s = a[1]
        if r == 1:
            return s
        per = 2 * (r - 1)
        res = []
        for row in range(r):
            for i, c in enumerate(s):
                m = i % per
                if min(m, per - m) == row:
                    res.append(c)
        return ''.join(res)
    return gen, sol, brute


@task('excel_column', 'Столбцы таблицы',
"""В таблице столбцы названы буквами: A, B, …, Z, затем AA, AB, …, AZ, BA, … и так далее (как в Excel). Для каждого запроса переведите название в номер или номер в название.

## Вход

В первой строке число запросов q (1 ≤ q ≤ 100000). В каждой из следующих q строк либо название столбца из заглавных латинских букв, либо его номер (от 1 до 2147483647).

## Выход

Для каждого запроса номер, если дано название, или название, если дан номер.""",
["4\nA\n28\nZY\n701"], sizes=MID, diff=25)
def _():
    def gen(n, rnd, k):
        out = []
        for _ in range(n):
            x = rnd.randint(1, 800 if k == 0 else rnd.choice([30, 800, 18000, 2147483647]))
            if rnd.random() < 0.5:
                out.append(str(x))
            else:
                t = ''
                while x:
                    x -= 1
                    t = chr(65 + x % 26) + t
                    x //= 26
                out.append(t)
        return str(n) + '\n' + '\n'.join(out) + '\n'

    def sol(inp):
        a = inp.split()
        q = int(a[0])
        out = []
        for w in a[1:q + 1]:
            if w.isdigit():
                x = int(w)
                t = ''
                while x:
                    x -= 1
                    t = chr(65 + x % 26) + t
                    x //= 26
                out.append(t)
            else:
                v = 0
                for c in w:
                    v = v * 26 + ord(c) - 64
                out.append(str(v))
        return '\n'.join(out)

    def brute(inp):
        a = inp.split()
        q = int(a[0])
        names = ['']
        cur = ['']
        for L in range(1, 4):
            nxt = []
            for p in cur:
                for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    nxt.append(p + c)
            names += nxt
            cur = nxt
        idx = {t: i for i, t in enumerate(names)}
        out = []
        for w in a[1:q + 1]:
            out.append(names[int(w)] if w.isdigit() else str(idx[w]))
        return '\n'.join(out)
    return gen, sol, brute


@task('look_say', 'Считай и называй',
"""Последовательность строк строится так: первая строка `1`. Каждая следующая описывает предыдущую: подряд идущие одинаковые цифры заменяются на их количество и саму цифру. Например, `1` → `11` (одна единица) → `21` (две единицы) → `1211` → `111221`. Выведите n-ю строку.

## Вход

Одно число n (1 ≤ n ≤ 40).

## Выход

n-я строка последовательности.""",
["1", "5"], sizes=[1, 2, 3, 5, 8, 12, 20, 30, 36, 40], diff=15)
def _():
    def gen(n, rnd, k):
        if k == 0:
            n = min(n, 12)
        return str(n) + '\n'

    def sol(inp):
        n = int(inp.split()[0])
        s = '1'
        for _ in range(n - 1):
            res = []
            i = 0
            while i < len(s):
                j = i
                while j < len(s) and s[j] == s[i]:
                    j += 1
                res.append(str(j - i) + s[i])
                i = j
            s = ''.join(res)
        return s

    def brute(inp):
        from itertools import groupby
        n = int(inp.split()[0])
        s = '1'
        for _ in range(n - 1):
            s = ''.join(str(len(list(g))) + k for k, g in groupby(s))
        return s
    return gen, sol, brute


@task('rle_pack', 'Сжатие повторов',
"""Слово сжимают так: каждую группу одинаковых подряд идущих букв заменяют на букву и число её повторений (даже если оно равно 1). Например, `aaabcc` превращается в `a3b1c2`. Выполните сжатие.

## Вход

Одна строка из строчных латинских букв, длина от 1 до 200000.

## Выход

Сжатая строка.""",
["aaabcc", "zzzz"], sizes=BIG, diff=10)
def _():
    def gen(n, rnd, k):
        al = 'ab' if k < 5 else 'abc'
        s = []
        while len(s) < n:
            s += [rnd.choice(al)] * rnd.randint(1, 5 if k < 9 else 1000)
        return ''.join(s[:n]) + '\n'

    def sol(inp):
        s = inp.split()[0]
        res = []
        i = 0
        while i < len(s):
            j = i
            while j < len(s) and s[j] == s[i]:
                j += 1
            res.append(s[i] + str(j - i))
            i = j
        return ''.join(res)

    def brute(inp):
        from itertools import groupby
        s = inp.split()[0]
        return ''.join(k + str(len(list(g))) for k, g in groupby(s))
    return gen, sol, brute


@task('shift_prefixes', 'Сдвиги начал',
"""Дано слово из строчных букв и n чисел x_1 … x_n. Для каждого i первые i букв слова сдвигаются по алфавиту вперёд на x_i позиций (после `z` идёт `a`). Найдите итоговое слово после всех сдвигов.

## Вход

В первой строке слово длины n (1 ≤ n ≤ 200000). Во второй строке n чисел x_i (0 ≤ x_i ≤ 10^9).

## Выход

Итоговое слово.""",
["abc\n3 5 9", "z\n1"], sizes=BIG, diff=20)
def _():
    def gen(n, rnd, k):
        s = ''.join(rnd.choice('abcxyz') for _ in range(n))
        return s + '\n' + ' '.join(str(rnd.randint(0, 10 ** 9)) for _ in range(n)) + '\n'

    def sol(inp):
        a = inp.split()
        s = a[0]
        n = len(s)
        x = [int(t) for t in a[1:n + 1]]
        tot = 0
        res = [''] * n
        for i in range(n - 1, -1, -1):
            tot = (tot + x[i]) % 26
            res[i] = chr((ord(s[i]) - 97 + tot) % 26 + 97)
        return ''.join(res)

    def brute(inp):
        a = inp.split()
        s = list(a[0])
        n = len(s)
        x = [int(t) for t in a[1:n + 1]]
        for i in range(n):
            for j in range(i + 1):
                s[j] = chr((ord(s[j]) - 97 + x[i]) % 26 + 97)
        return ''.join(s)
    return gen, sol, brute


@task('parse_int', 'Чтение числа',
"""Программа читает число из начала строки так: сначала пропускает ведущие пробелы, затем читает необязательный знак `+` или `-`, затем подряд идущие цифры; на первом другом символе чтение заканчивается. Если цифр нет, результат 0. Если число выходит за диапазон от −2147483648 до 2147483647, оно заменяется ближайшей границей диапазона.

## Вход

В первой строке число q (1 ≤ q ≤ 100000). В следующих q строках по одной строке из латинских букв, цифр, пробелов, `+`, `-`, `.`, длиной от 1 до 40 (в каждой есть хотя бы один символ, не являющийся пробелом).

## Выход

Для каждой строки прочитанное число.""",
["4\n   -42\n4193 with words\nwords and 987\n-91283472332"], sizes=MID, diff=20)
def _():
    def gen(n, rnd, k):
        out = []
        for _ in range(n):
            s = ' ' * rnd.randint(0, 3)
            s += rnd.choice(['', '', '+', '-', '--', '+-'])
            s += ''.join(rnd.choice('0123456789') for _ in range(rnd.choice([0, 1, 3, 9, 10, 12, 20])))
            s += rnd.choice(['', ' x', 'abc', '.5', ' 12', '-3'])
            if not s.strip():
                s = 'q'
            out.append(s)
        return str(n) + '\n' + '\n'.join(out) + '\n'

    def sol(inp):
        lines = inp.split('\n')
        q = int(lines[0])
        out = []
        for line in lines[1:q + 1]:
            i = 0
            n = len(line)
            while i < n and line[i] == ' ':
                i += 1
            sg = 1
            if i < n and line[i] in '+-':
                if line[i] == '-':
                    sg = -1
                i += 1
            v = 0
            while i < n and '0' <= line[i] <= '9':
                v = v * 10 + ord(line[i]) - 48
                if v > 2 ** 31:
                    v = 2 ** 31
                i += 1
            v *= sg
            v = max(-2 ** 31, min(2 ** 31 - 1, v))
            out.append(str(v))
        return '\n'.join(out)

    def brute(inp):
        import re
        lines = inp.split('\n')
        q = int(lines[0])
        out = []
        for line in lines[1:q + 1]:
            m = re.match(r' *([+-]?)([0-9]+)', line)
            if not m:
                out.append('0')
                continue
            v = int(m.group(2))
            if m.group(1) == '-':
                v = -v
            out.append(str(max(-2 ** 31, min(2 ** 31 - 1, v))))
        return '\n'.join(out)
    return gen, sol, brute


@task('word_ladder_build', 'Слово по буквам',
"""Айдай составляет слова по одной букве: слово можно «построить», если оно состоит из одной буквы, которая есть в списке, или получается из построенного слова дописыванием одной буквы в конец, и само есть в списке. Найдите самое длинное построенное слово. Если таких несколько, выберите лексикографически наименьшее.

## Вход

В первой строке число n (1 ≤ n ≤ 100000). Затем n различных слов из строчных латинских букв через пробел или с новой строки. Суммарная длина слов не больше 300000.

## Выход

Самое длинное построенное слово или `-`, если построенных слов нет.""",
["5\nw wo wor worl world", "3\nab abc b"],
sizes=[3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000], diff=35)
def _():
    def gen(n, rnd, k):
        words = set()
        al = 'ab'
        tries = 0
        while len(words) < n and tries < n * 5:
            tries += 1
            if words and rnd.random() < 0.7:
                w = rnd.choice(sorted(words)) if len(words) < 50 else rnd.choice(list(words))
                if len(w) < 12:
                    words.add(w + rnd.choice(al))
                    continue
            words.add(''.join(rnd.choice(al) for _ in range(rnd.randint(1, 8))))
        ws = sorted(words)
        rnd.shuffle(ws)
        return str(len(ws)) + '\n' + ' '.join(ws) + '\n'

    def sol(inp):
        a = inp.split()
        n = int(a[0])
        ws = sorted(set(a[1:n + 1]), key=lambda w: (len(w), w))
        ok = set()
        best = '-'
        for w in ws:
            if len(w) == 1 or w[:-1] in ok:
                ok.add(w)
                if best == '-' or len(w) > len(best):
                    best = w
        return best

    def brute(inp):
        a = inp.split()
        n = int(a[0])
        st = set(a[1:n + 1])
        best = '-'
        for w in sorted(st):
            if all(w[:i] in st for i in range(1, len(w) + 1)):
                if best == '-' or len(w) > len(best):
                    best = w
        return best
    return gen, sol, brute
