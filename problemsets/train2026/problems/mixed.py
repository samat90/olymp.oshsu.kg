import heapq
from collections import deque, defaultdict
from lib import P, size, nums

PROBLEMS = []
MOD = 10 ** 9 + 7


def add(*a, **k):
    PROBLEMS.append(P(*a, **k))


def word(r, n, alpha):
    return ''.join(r.choice(alpha) for _ in range(n))


# ---------- longest substring without repeats ----------
def gen(r, lv):
    n = size(lv, 100000)
    return word(r, n, 'abc' if lv < 3 else ('abcdefghijklmnopqrstuvwxyz' if lv % 2 else 'abcdefghijklmnopqrstuvwxyz0123456789')) + '\n'


def solve(d):
    s = d.split()[0]; last = {}; j = best = 0
    for i, c in enumerate(s):
        if c in last and last[c] >= j:
            j = last[c] + 1
        last[c] = i; best = max(best, i - j + 1)
    return str(best)


def brute(d):
    s = d.split()[0]; best = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            if len(set(s[i:j + 1])) == j - i + 1:
                best = max(best, j - i + 1)
    return str(best)


add('unique_pattern', 'Узор на кошме', 'training', ['Строки'], 32, """
# Узор на кошме

Мастерица Гульнара вышивает на кошме строку из символов-узоров. Она хочет вырезать самый длинный кусок из **подряд идущих** символов, в котором все символы **различны**. Найдите его длину.

## Формат ввода

В единственной строке записана непустая строка $s$ из строчных латинских букв и цифр ($1 \\le |s| \\le 10^5$).

## Формат вывода

Выведите длину наибольшей подстроки без повторяющихся символов.
""", ['abcabcbb\n', 'bbbbb\n'], gen, solve, brute)


# ---------- brackets of three kinds ----------
def gen(r, lv):
    n = size(lv, 100000) // 2 * 2 or 2
    pairs = '()[]{}'
    if r.random() < 0.5 or lv < 2:
        s = [r.choice(pairs) for _ in range(n)]
    else:
        st, s = [], []
        for i in range(n):
            if st and (len(st) >= n - i or r.random() < 0.5):
                s.append({'(': ')', '[': ']', '{': '}'}[st.pop()])
            else:
                c = r.choice('([{'); st.append(c); s.append(c)
        if lv % 2 and s:
            s[r.randrange(n)] = r.choice(pairs)
    return ''.join(s) + '\n'


def solve(d):
    s = d.split()[0]; st = []; m = {')': '(', ']': '[', '}': '{'}
    for c in s:
        if c in '([{':
            st.append(c)
        else:
            if not st or st.pop() != m[c]:
                return 'NO'
    return 'NO' if st else 'YES'


def brute(d):
    s = d.split()[0]
    while True:
        t = s.replace('()', '').replace('[]', '').replace('{}', '')
        if t == s:
            break
        s = t
    return 'YES' if s == '' else 'NO'


add('ornament_brackets', 'Скобки в орнаменте', 'training', ['Строки', 'Структуры данных'], 26, """
# Скобки в орнаменте

Орнамент на сундуке записан строкой из скобок трёх видов: `()`, `[]`, `{}`. Орнамент считается правильным, если каждой открывающей скобке соответствует закрывающая **того же вида**, а пары вложены друг в друга без пересечений (например, `{[()]}` правильный, а `([)]` — нет). Пустая строка тоже правильная.

## Формат ввода

В единственной строке записана непустая строка из символов `()[]{}` длиной не более $10^5$.

## Формат вывода

Выведите `YES`, если орнамент правильный, и `NO` иначе.
""", ['{[()]}\n', '([)]\n'], gen, solve, brute)


# ---------- coin change ----------
def gen(r, lv):
    k = r.randint(1, 3 if lv < 3 else 8)
    top = 12 if lv < 3 else 100
    c = sorted(set(r.randint(1, top) for _ in range(k)))
    s = r.randint(0, 20) if lv < 3 else size(lv, 10 ** 5)
    return '%d %d\n%s\n' % (len(c), s, nums(c))


def solve(d):
    t = list(map(int, d.split())); k, s = t[0], t[1]; c = t[2:2 + k]
    INF = 10 ** 9; f = [0] + [INF] * s
    for v in range(1, s + 1):
        for x in c:
            if x <= v and f[v - x] + 1 < f[v]:
                f[v] = f[v - x] + 1
    return str(f[s] if f[s] < INF else -1)


def brute(d):
    t = list(map(int, d.split())); k, s = t[0], t[1]; c = t[2:2 + k]
    seen = {0}; q = deque([(0, 0)])
    while q:
        v, dist = q.popleft()
        if v == s:
            return str(dist)
        for x in c:
            if v + x <= s and v + x not in seen:
                seen.add(v + x); q.append((v + x, dist + 1))
    return '-1'


add('som_coins', 'Сомы для базара', 'training', ['DP'], 34, """
# Сомы для базара

В кошельке Нурлана неограниченно много монет $k$ номиналов $c_1, \\dots, c_k$ сомов. Какое наименьшее количество монет нужно, чтобы расплатиться ровно на $S$ сомов? Если это невозможно — выведите $-1$.

## Формат ввода

В первой строке записаны $k$ и $S$ ($1 \\le k \\le 8$, $0 \\le S \\le 10^5$). Во второй строке — $k$ различных натуральных номиналов $c_i \\le 100$.

## Формат вывода

Выведите наименьшее число монет либо $-1$. При $S = 0$ ответ равен $0$.
""", ['3 11\n1 2 5\n', '1 3\n2\n'], gen, solve, brute)


# ---------- 0/1 knapsack ----------
def gen(r, lv):
    n = r.randint(1, 8) if lv < 3 else size(lv, 200)
    w = [r.randint(1, 10 if lv < 3 else 50) for _ in range(n)]
    v = [r.randint(1, 20 if lv < 3 else 10 ** 6) for _ in range(n)]
    W = r.randint(1, 25) if lv < 3 else r.randint(10, 5000)
    return '%d %d\n' % (n, W) + ''.join('%d %d\n' % x for x in zip(w, v))


def solve(d):
    t = list(map(int, d.split())); n, W = t[0], t[1]; f = [0] * (W + 1)
    for i in range(n):
        w, v = t[2 + 2 * i], t[3 + 2 * i]
        for j in range(W, w - 1, -1):
            if f[j - w] + v > f[j]:
                f[j] = f[j - w] + v
    return str(f[W])


def brute(d):
    t = list(map(int, d.split())); n, W = t[0], t[1]; best = 0
    for m in range(1 << n):
        sw = sv = 0
        for i in range(n):
            if m >> i & 1:
                sw += t[2 + 2 * i]; sv += t[3 + 2 * i]
        if sw <= W:
            best = max(best, sv)
    return str(best)


add('yak_knapsack', 'Рюкзак торговца яками', 'training', ['DP'], 38, """
# Рюкзак торговца яками

Торговец собирает в дорогу товары. Есть $n$ видов товаров, каждый — в единственном экземпляре: $i$-й весит $w_i$ кг и приносит $v_i$ сомов прибыли. Як выдержит не больше $W$ кг. Какую наибольшую суммарную прибыль можно увезти?

## Формат ввода

В первой строке записаны $n$ и $W$ ($1 \\le n \\le 200$, $1 \\le W \\le 5000$). В следующих $n$ строках записаны $w_i$ и $v_i$ ($1 \\le w_i \\le 50$, $1 \\le v_i \\le 10^6$).

## Формат вывода

Выведите наибольшую суммарную прибыль.
""", ['3 5\n2 30\n3 40\n4 50\n'], gen, solve, brute)


# ---------- edit distance ----------
def gen(r, lv):
    n = r.randint(1, 6) if lv < 3 else size(lv, 1500)
    m = r.randint(1, 6) if lv < 3 else size(lv, 1500)
    al = 'ab' if lv < 3 else 'abcdefgh'
    return word(r, n, al) + '\n' + word(r, m, al) + '\n'


def solve(d):
    a, b = d.split()[:2]; prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return str(prev[-1])


def brute(d):
    a, b = d.split()[:2]
    from functools import lru_cache

    @lru_cache(None)
    def f(i, j):
        if i == len(a): return len(b) - j
        if j == len(b): return len(a) - i
        if a[i] == b[j]: return f(i + 1, j + 1)
        return 1 + min(f(i + 1, j), f(i, j + 1), f(i + 1, j + 1))
    return str(f(0, 0))


add('name_fix', 'Исправление имён в списке', 'olympiad', ['Строки', 'DP'], 46, """
# Исправление имён в списке

В списке участников олимпиады имя записано с ошибками. Разрешены операции над строкой: вставить символ, удалить символ или заменить один символ другим. Какое наименьшее количество операций превращает строку $a$ в строку $b$?

## Формат ввода

В первой строке записана строка $a$, во второй — строка $b$. Строки непусты, состоят из строчных латинских букв, длина каждой не больше $1500$.

## Формат вывода

Выведите наименьшее число операций.
""", ['kitten\nsitting\n', 'ala\nala\n'], gen, solve, brute, time=2)


# ---------- longest palindromic substring ----------
def gen(r, lv):
    n = size(lv, 2000)
    al = 'ab' if lv % 2 == 0 else 'abc'
    if lv >= 3 and lv % 3 == 0:
        return 'a' * n + '\n'
    return word(r, n, al) + '\n'


def solve(d):
    s = d.split()[0]; n = len(s); best = 1
    for c in range(n):
        for l, r_ in ((c, c), (c, c + 1)):
            while l >= 0 and r_ < n and s[l] == s[r_]:
                l -= 1; r_ += 1
            best = max(best, r_ - l - 1)
    return str(best)


def brute(d):
    s = d.split()[0]
    return str(max(j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1) if s[i:j] == s[i:j][::-1]))


add('toast_palindrome', 'Тост-перевёртыш', 'training', ['Строки'], 36, """
# Тост-перевёртыш

Тамада записал тост строкой $s$. Слушатели радуются, когда кусок тоста читается одинаково слева направо и справа налево. Найдите длину самой длинной такой **подстроки** (подряд идущих символов).

## Формат ввода

В единственной строке записана строка $s$ из строчных латинских букв, $1 \\le |s| \\le 2000$.

## Формат вывода

Выведите длину наибольшего палиндрома среди подстрок.
""", ['babad\n', 'abc\n'], gen, solve, brute)


# ---------- grid: islands ----------
def grid(r, lv):
    h = r.randint(1, 4) if lv < 3 else size(lv, 400)
    w = r.randint(1, 4) if lv < 3 else size(lv, 400)
    p = r.choice([0.3, 0.5, 0.65])
    return h, w, [''.join('#' if r.random() < p else '.' for _ in range(w)) for _ in range(h)]


def gen(r, lv):
    h, w, g = grid(r, lv)
    return '%d %d\n%s\n' % (h, w, '\n'.join(g))


def solve(d):
    t = d.split(); h, w = int(t[0]), int(t[1]); g = [list(x) for x in t[2:2 + h]]; cnt = 0
    for i in range(h):
        for j in range(w):
            if g[i][j] == '#':
                cnt += 1; g[i][j] = '.'; st = [(i, j)]
                while st:
                    x, y = st.pop()
                    for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= a < h and 0 <= b < w and g[a][b] == '#':
                            g[a][b] = '.'; st.append((a, b))
    return str(cnt)


def brute(d):
    t = d.split(); h, w = int(t[0]), int(t[1]); g = t[2:2 + h]
    cells = {(i, j) for i in range(h) for j in range(w) if g[i][j] == '#'}
    comp = {c: c for c in cells}

    def find(x):
        while comp[x] != x:
            x = comp[x]
        return x
    for (i, j) in cells:
        for nb in ((i + 1, j), (i, j + 1)):
            if nb in cells:
                comp[find(nb)] = find((i, j))
    return str(len({find(c) for c in cells}))


add('issyk_islands', 'Острова Иссык-Куля', 'training', ['Графы'], 30, """
# Острова Иссык-Куля

На карте озера Иссык-Куль размером $h \\times w$ клеток символ `#` — суша, `.` — вода. Два участка суши относятся к одному острову, если их можно соединить цепочкой клеток суши, где соседние клетки имеют общую **сторону** (по диагонали переходить нельзя). Сколько островов на карте?

## Формат ввода

В первой строке записаны $h$ и $w$ ($1 \\le h, w \\le 400$). Далее $h$ строк по $w$ символов `#` или `.`.

## Формат вывода

Выведите количество островов.
""", ['3 4\n##..\n#..#\n..##\n', '2 2\n..\n..\n'], gen, solve, brute)


# ---------- grid: shortest path ----------
def gen(r, lv):
    h = r.randint(1, 5) if lv < 3 else size(lv, 500)
    w = r.randint(1, 5) if lv < 3 else size(lv, 500)
    p = r.choice([0.1, 0.2, 0.3])
    g = [['#' if r.random() < p else '.' for _ in range(w)] for _ in range(h)]
    g[0][0] = '.'; g[h - 1][w - 1] = '.'
    return '%d %d\n%s\n' % (h, w, '\n'.join(''.join(x) for x in g))


def bfs_grid(d):
    t = d.split(); h, w = int(t[0]), int(t[1]); g = t[2:2 + h]
    dist = {(0, 0): 0}; q = deque([(0, 0)])
    while q:
        x, y = q.popleft()
        for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= a < h and 0 <= b < w and g[a][b] == '.' and (a, b) not in dist:
                dist[(a, b)] = dist[(x, y)] + 1; q.append((a, b))
    return str(dist.get((h - 1, w - 1), -1))


def brute(d):  # Bellman-Ford style relaxation on the grid
    t = d.split(); h, w = int(t[0]), int(t[1]); g = t[2:2 + h]
    INF = 10 ** 9; f = [[INF] * w for _ in range(h)]; f[0][0] = 0; ch = True
    while ch:
        ch = False
        for i in range(h):
            for j in range(w):
                if g[i][j] != '.': continue
                for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                    if 0 <= a < h and 0 <= b < w and g[a][b] == '.' and f[a][b] + 1 < f[i][j]:
                        f[i][j] = f[a][b] + 1; ch = True
    return str(f[h - 1][w - 1] if f[h - 1][w - 1] < INF else -1)


add('alaarcha_trail', 'Тропа в Ала-Арче', 'training', ['Графы'], 32, """
# Тропа в Ала-Арче

Туристы идут по карте ущелья размером $h \\times w$ клеток: `.` — свободная клетка, `#` — скала. За один шаг можно перейти в соседнюю по стороне свободную клетку. Найдите наименьшее число шагов от левого верхнего угла до правого нижнего (обе эти клетки свободны) или выведите $-1$, если пути нет.

## Формат ввода

В первой строке записаны $h$ и $w$ ($1 \\le h, w \\le 500$). Далее $h$ строк по $w$ символов `.` или `#`.

## Формат вывода

Выведите длину кратчайшего пути.
""", ['3 3\n...\n.#.\n...\n', '2 2\n.#\n#.\n'], gen, bfs_grid, brute)


# ---------- dijkstra ----------
def gen(r, lv):
    n = r.randint(2, 6) if lv < 3 else size(lv, 50000)
    m = r.randint(1, 10) if lv < 3 else min(2 * n, 100000)
    hi = 10 if lv < 3 else 10 ** 6
    e = [(r.randint(1, n), r.randint(1, n), r.randint(1, hi)) for _ in range(m)]
    return '%d %d\n' % (n, m) + ''.join('%d %d %d\n' % x for x in e)


def solve(d):
    t = list(map(int, d.split())); n, m = t[0], t[1]; adj = [[] for _ in range(n + 1)]
    for i in range(m):
        a, b, c = t[2 + 3 * i:5 + 3 * i]; adj[a].append((b, c)); adj[b].append((a, c))
    INF = float('inf'); dist = [INF] * (n + 1); dist[1] = 0; pq = [(0, 1)]
    while pq:
        dv, v = heapq.heappop(pq)
        if dv > dist[v]: continue
        for u, c in adj[v]:
            if dv + c < dist[u]:
                dist[u] = dv + c; heapq.heappush(pq, (dist[u], u))
    return str(dist[n] if dist[n] < INF else -1)


def brute(d):
    t = list(map(int, d.split())); n, m = t[0], t[1]
    INF = float('inf'); dist = [INF] * (n + 1); dist[1] = 0
    for _ in range(n):
        for i in range(m):
            a, b, c = t[2 + 3 * i:5 + 3 * i]
            if dist[a] + c < dist[b]: dist[b] = dist[a] + c
            if dist[b] + c < dist[a]: dist[a] = dist[b] + c
    return str(dist[n] if dist[n] < INF else -1)


add('kg_roads', 'Дороги Кыргызстана', 'olympiad', ['Графы'], 44, """
# Дороги Кыргызстана

В стране $n$ городов, пронумерованных от $1$ до $n$, и $m$ двусторонних дорог, у каждой есть длина в километрах. Между парой городов может быть несколько дорог, встречаются и петли. Найдите длину кратчайшего пути из города $1$ (Бишкек) в город $n$ (Ош) или выведите $-1$, если проехать нельзя.

## Формат ввода

В первой строке записаны $n$ и $m$ ($2 \\le n \\le 5 \\cdot 10^4$, $1 \\le m \\le 10^5$). В следующих $m$ строках записаны $a_i$, $b_i$, $c_i$ — концы дороги и её длина ($1 \\le c_i \\le 10^6$).

## Формат вывода

Выведите длину кратчайшего пути или $-1$.
""", ['4 4\n1 2 5\n2 4 5\n1 3 1\n3 4 20\n', '3 1\n1 2 7\n'], gen, solve, brute, time=2)


# ---------- DSU components with queries ----------
def gen(r, lv):
    n = r.randint(2, 6) if lv < 3 else size(lv, 100000)
    q = r.randint(1, 10) if lv < 3 else size(lv, 100000)
    ops = []
    for _ in range(q):
        ops.append('%d %d %d' % (r.choice((1, 2)), r.randint(1, n), r.randint(1, n)))
    return '%d %d\n%s\n' % (n, q, '\n'.join(ops))


def solve(d):
    t = list(map(int, d.split())); n, q = t[0], t[1]; p = list(range(n + 1)); out = []

    def find(x):
        while p[x] != x:
            p[x] = p[p[x]]; x = p[x]
        return x
    for i in range(q):
        k, a, b = t[2 + 3 * i:5 + 3 * i]
        if k == 1:
            p[find(a)] = find(b)
        else:
            out.append('YES' if find(a) == find(b) else 'NO')
    return '\n'.join(out)


def brute(d):
    t = list(map(int, d.split())); n, q = t[0], t[1]; adj = defaultdict(set); out = []
    for i in range(q):
        k, a, b = t[2 + 3 * i:5 + 3 * i]
        if k == 1:
            adj[a].add(b); adj[b].add(a)
        else:
            seen = {a}; st = [a]
            while st:
                v = st.pop()
                for u in adj[v]:
                    if u not in seen:
                        seen.add(u); st.append(u)
            out.append('YES' if b in seen else 'NO')
    return '\n'.join(out)


add('aiyl_unions', 'Союзы айылов', 'training', ['Графы', 'Структуры данных'], 40, """
# Союзы айылов

Есть $n$ айылов, сначала каждый сам по себе. Поступают $q$ запросов:

- `1 a b` — айылы $a$ и $b$ объединяют свои союзы в один;
- `2 a b` — нужно ответить, состоят ли $a$ и $b$ в одном союзе (напрямую или через цепочку объединений).

## Формат ввода

В первой строке записаны $n$ и $q$ ($2 \\le n \\le 10^5$, $1 \\le q \\le 10^5$). В следующих $q$ строках записаны тип запроса $k$ и числа $a$, $b$ ($1 \\le a, b \\le n$).

## Формат вывода

На каждый запрос типа $2$ выведите `YES` или `NO` в отдельной строке. Если таких запросов нет, ничего не выводите.
""", ['4 5\n1 1 2\n2 1 2\n2 1 3\n1 2 3\n2 1 3\n'], gen, solve, brute)


# ---------- Nim ----------
def gen(r, lv):
    n = r.randint(1, 4) if lv < 3 else size(lv, 100000)
    hi = 4 if lv < 3 else 10 ** 9
    return '%d\n%s\n' % (n, nums([r.randint(1, hi) for _ in range(n)]))


def solve(d):
    t = list(map(int, d.split())); x = 0
    for v in t[1:1 + t[0]]:
        x ^= v
    return 'Aibek' if x else 'Bermet'


def brute(d):
    t = list(map(int, d.split())); from functools import lru_cache

    @lru_cache(None)
    def win(state):
        for i, v in enumerate(state):
            for k in range(1, v + 1):
                ns = tuple(sorted(state[:i] + (v - k,) + state[i + 1:]))
                if not win(ns):
                    return True
        return False
    return 'Aibek' if win(tuple(sorted(t[1:1 + t[0]]))) else 'Bermet'


add('stone_game', 'Игра в камни у костра', 'training', ['Теория игр', 'Математика'], 33, """
# Игра в камни у костра

Айбек и Бермет играют у костра. На земле лежат $n$ кучек камней. Игроки ходят по очереди, начинает Айбек. За ход нужно выбрать **одну** кучку и взять из неё любое положительное количество камней. Кто не может сделать ход — проигрывает. Оба играют наилучшим образом. Кто победит?

## Формат ввода

В первой строке записано $n$ ($1 \\le n \\le 10^5$). Во второй строке — $n$ чисел $a_i$ — размеры кучек ($1 \\le a_i \\le 10^9$).

## Формат вывода

Выведите `Aibek`, если побеждает Айбек, и `Bermet` иначе.
""", ['3\n1 2 3\n', '2\n5 4\n'], gen, solve, brute)


# ---------- trailing zeros ----------
def gen(r, lv):
    n = r.randint(1, 30) if lv < 3 else [10 ** 3, 10 ** 5, 10 ** 7, 10 ** 9, 10 ** 12, 10 ** 15, 10 ** 18][lv - 3 if lv < 9 else 6]
    if lv >= 3:
        n = r.randint(n // 2, n)
    return '%d\n' % n


def solve(d):
    n = int(d.split()[0]); c = 0
    while n:
        n //= 5; c += n
    return str(c)


def brute(d):
    n = int(d.split()[0]); f = 1
    for i in range(2, n + 1): f *= i
    s = str(f)
    return str(len(s) - len(s.rstrip('0')))


add('factorial_zeros', 'Нули в числе мешков', 'training', ['Математика', 'Теория чисел'], 22, """
# Нули в числе мешков

Торговец перемножил числа от $1$ до $n$ и получил огромное число мешков $n!$. Сколько нулей стоит в конце его десятичной записи?

## Формат ввода

В единственной строке записано $n$ ($1 \\le n \\le 10^{18}$).

## Формат вывода

Выведите количество нулей в конце числа $n!$.
""", ['5\n', '100\n'], gen, solve, brute)


# ---------- binomial mod p ----------
def gen(r, lv):
    q = r.randint(1, 5) if lv < 3 else size(lv, 100000)
    top = 10 if lv < 3 else 10 ** 6
    ps = []
    for _ in range(q):
        n = r.randint(0, top); ps.append((n, r.randint(0, n)))
    return '%d\n%s' % (q, ''.join('%d %d\n' % p for p in ps))


def solve(d):
    t = list(map(int, d.split())); q = t[0]; top = max(t[1::2][:q]) + 1
    f = [1] * (top + 1)
    for i in range(1, top + 1): f[i] = f[i - 1] * i % MOD
    inv = [1] * (top + 1); inv[top] = pow(f[top], MOD - 2, MOD)
    for i in range(top, 0, -1): inv[i - 1] = inv[i] * i % MOD
    return '\n'.join(str(f[n] * inv[k] % MOD * inv[n - k] % MOD) for n, k in zip(t[1::2][:q], t[2::2][:q]))


def brute(d):
    t = list(map(int, d.split())); q = t[0]; out = []
    for i in range(q):
        n, k = t[1 + 2 * i], t[2 + 2 * i]; row = [1]
        for _ in range(n):
            row = [1] + [(row[j] + row[j + 1]) % MOD for j in range(len(row) - 1)] + [1]
        out.append(str(row[k]))
    return '\n'.join(out)


add('seating_binom', 'Почётный стол на тое', 'olympiad', ['Комбинаторика', 'Математика'], 42, """
# Рассадка гостей на тое

Из $n$ гостей нужно выбрать $k$ человек, которые сядут за почётный стол (порядок не важен). Сколькими способами это можно сделать? Для каждого из $q$ запросов выведите ответ по модулю $10^9 + 7$.

## Формат ввода

В первой строке записано $q$ ($1 \\le q \\le 10^5$). В следующих $q$ строках записаны $n$ и $k$ ($0 \\le k \\le n \\le 10^6$).

## Формат вывода

Выведите $q$ чисел — по одному в строке: $C(n, k) \\bmod (10^9 + 7)$.
""", ['3\n5 2\n10 0\n6 6\n'], gen, solve, brute)


# ---------- polygon area ----------
def gen(r, lv):
    n = r.randint(3, 6) if lv < 3 else size(lv, 50000)
    import math
    hi = 10 if lv < 3 else 10 ** 6
    ang = sorted(r.uniform(0, 2 * math.pi) for _ in range(n))
    pts = [(int(math.cos(a) * r.randint(hi // 2, hi)), int(math.sin(a) * r.randint(hi // 2, hi))) for a in ang]
    return '%d\n%s' % (n, ''.join('%d %d\n' % p for p in pts))


def solve(d):
    t = list(map(int, d.split())); n = t[0]; p = [(t[1 + 2 * i], t[2 + 2 * i]) for i in range(n)]
    s = sum(p[i][0] * p[(i + 1) % n][1] - p[(i + 1) % n][0] * p[i][1] for i in range(n))
    return str(abs(s))


def brute(d):  # trapezoids under each edge
    t = list(map(int, d.split())); n = t[0]; p = [(t[1 + 2 * i], t[2 + 2 * i]) for i in range(n)]
    s = sum((p[(i + 1) % n][0] - p[i][0]) * (p[(i + 1) % n][1] + p[i][1]) for i in range(n))
    return str(abs(s))


add('field_area', 'Площадь поля у Чолпон-Аты', 'training', ['Геометрия'], 28, """
# Площадь поля у Чолпон-Аты

Поле имеет форму многоугольника без самопересечений. Вершины заданы целыми координатами в порядке обхода (по или против часовой стрелки). Выведите **удвоенную** площадь поля — это всегда целое число.

## Формат ввода

В первой строке записано $n$ ($3 \\le n \\le 5 \\cdot 10^4$). В следующих $n$ строках записаны координаты $x_i$, $y_i$ ($|x_i|, |y_i| \\le 10^6$).

## Формат вывода

Выведите удвоенную площадь многоугольника.
""", ['4\n0 0\n4 0\n4 3\n0 3\n', '3\n0 0\n1 0\n0 1\n'], gen, solve, brute)


# ---------- word frequency ----------
def gen(r, lv):
    n = r.randint(1, 8) if lv < 3 else size(lv, 100000)
    voc = ['ala', 'too', 'kol', 'jol', 'suu', 'tash', 'bulak', 'kyrgyz'] if lv < 5 else [word(r, r.randint(1, 6), 'abc') for _ in range(max(2, n // 20))]
    return '%d\n%s\n' % (n, ' '.join(r.choice(voc) for _ in range(n)))


def solve(d):
    t = d.split(); n = int(t[0]); c = defaultdict(int)
    for w in t[1:1 + n]: c[w] += 1
    best = max(c.values())
    return min(w for w in c if c[w] == best) + ' ' + str(best)


def brute(d):
    t = d.split(); n = int(t[0]); ws = t[1:1 + n]
    res = sorted(set(ws), key=lambda w: (-ws.count(w), w))[0]
    return res + ' ' + str(ws.count(res))


add('popular_word', 'Любимое слово манасчи', 'training', ['Строки', 'Сортировка'], 16, """
# Любимое слово манасчи

В записи сказания встречается $n$ слов. Найдите слово, которое встречается чаще всех; если таких несколько, выберите лексикографически наименьшее (по кодам символов).

## Формат ввода

В первой строке записано $n$ ($1 \\le n \\le 10^5$). Во второй строке — $n$ слов из строчных латинских букв, длина каждого не больше $10$, через пробел.

## Формат вывода

Выведите слово и через пробел количество его вхождений.
""", ['5\nala too ala jol too\n'], gen, solve, brute)
