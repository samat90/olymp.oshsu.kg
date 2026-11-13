import heapq
import itertools
import math
from collections import deque, defaultdict
from functools import lru_cache
from lib import prob, size, nums, ints

MOD = 10 ** 9 + 7


def edges(r, n, m, directed=False, wmax=None, simple=True):
    seen = set(); res = []
    for _ in range(m * 3):
        if len(res) >= m: break
        a, b = r.randint(1, n), r.randint(1, n)
        if simple and a == b: continue
        k = (a, b) if directed else (min(a, b), max(a, b))
        if simple and k in seen: continue
        seen.add(k); res.append((a, b) if wmax is None else (a, b, r.randint(1, wmax)))
    return res


def fmt(n, es):
    return '%d %d\n%s' % (n, len(es), ''.join(' '.join(map(str, e)) + '\n' for e in es))


@prob('exam_order', 'Порядок зачётов', 'training', ['Графы'], 34,
      r"В ОшГУ $n$ зачётов, пронумерованных от $1$ до $n$. Для $m$ пар $(a, b)$ зачёт $a$ нужно сдать **до** зачёта $b$. Можно ли сдать все зачёты по одному, не нарушив ни одного условия?",
      r"В первой строке $n$ и $m$ ($1 \le n, m \le 10^5$). Далее $m$ строк с $a_i$, $b_i$ ($1 \le a_i, b_i \le n$).",
      r"`YES` или `NO`.", ['3 2\n1 2\n2 3\n', '2 2\n1 2\n2 1\n'])
class _:
    def gen(r, lv):
        n = r.randint(1, 6) if lv < 3 else size(lv, 10 ** 5); m = r.randint(1, 8) if lv < 3 else min(2 * n, 10 ** 5)
        perm = list(range(1, n + 1)); r.shuffle(perm)
        es = []
        for _ in range(m):
            i, j = r.randint(0, n - 1), r.randint(0, n - 1)
            if i != j: es.append((perm[min(i, j)], perm[max(i, j)]))
        if r.random() < 0.5 and es: es.append((es[0][1], es[0][0]))
        if not es: es = [(1, 1)]
        return fmt(n, es)

    def solve(d):
        t = ints(d); n, m = t[0], t[1]; adj = [[] for _ in range(n + 1)]; deg = [0] * (n + 1)
        for i in range(m):
            adj[t[2 + 2 * i]].append(t[3 + 2 * i]); deg[t[3 + 2 * i]] += 1
        q = [v for v in range(1, n + 1) if deg[v] == 0]; seen = 0
        while q:
            v = q.pop(); seen += 1
            for u in adj[v]:
                deg[u] -= 1
                if deg[u] == 0: q.append(u)
        return 'YES' if seen == n else 'NO'

    def brute(d):
        t = ints(d); n, m = t[0], t[1]; es = [(t[2 + 2 * i], t[3 + 2 * i]) for i in range(m)]
        for p in itertools.permutations(range(1, n + 1)):
            pos = {v: i for i, v in enumerate(p)}
            if all(pos[a] < pos[b] for a, b in es): return 'YES'
        return 'NO'


@prob('apricots', 'Созревание абрикосов', 'training', ['Графы'], 36,
      r"В саду $h \times w$ клеток: `0` — пусто, `1` — свежий абрикос, `2` — гнилой. Каждую минуту гнилой абрикос портит все свежие в четырёх соседних по стороне клетках. За сколько минут сгниют все абрикосы? Если какой-то свежий абрикос никогда не сгниёт, выведите $-1$. Если свежих нет, ответ $0$.",
      r"В первой строке $h$ и $w$ ($1 \le h, w \le 500$). Далее $h$ строк из символов `0`, `1`, `2`.",
      r"Число минут или $-1$.", ['3 3\n211\n110\n011\n', '1 2\n21\n'.replace('21', '20').replace('1 2', '1 2')])
class _:
    def gen(r, lv):
        h = r.randint(1, 4) if lv < 3 else size(lv, 500); w = r.randint(1, 4) if lv < 3 else size(lv, 500)
        wts = [1, 6, 1] if lv % 2 else [2, 8, 1]
        return '%d %d\n%s\n' % (h, w, '\n'.join(''.join(r.choices('012', wts, k=w)) for _ in range(h)))

    def solve(d):
        t = d.split(); h, w = int(t[0]), int(t[1]); g = [list(x) for x in t[2:2 + h]]
        q = deque((i, j) for i in range(h) for j in range(w) if g[i][j] == '2'); fresh = sum(r_.count('1') for r_ in g); mins = 0
        while q and fresh:
            for _ in range(len(q)):
                x, y = q.popleft()
                for a, b in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= a < h and 0 <= b < w and g[a][b] == '1':
                        g[a][b] = '2'; fresh -= 1; q.append((a, b))
            mins += 1
        return str(mins if not fresh else -1)

    def brute(d):
        t = d.split(); h, w = int(t[0]), int(t[1]); g = [list(x) for x in t[2:2 + h]]; mins = 0
        while any('1' in r_ for r_ in g):
            ng = [r_[:] for r_ in g]; ch = False
            for i in range(h):
                for j in range(w):
                    if g[i][j] == '1' and any(0 <= a < h and 0 <= b < w and g[a][b] == '2' for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1))):
                        ng[i][j] = '2'; ch = True
            if not ch: return '-1'
            g = ng; mins += 1
        return str(mins)


@prob('two_teams', 'Две команды', 'training', ['Графы'], 38,
      r"В лагере $n$ детей, и некоторые пары в ссоре. Можно ли разбить детей на две команды так, чтобы ни в одной команде не было двух поссорившихся? (Команда может быть пустой.)",
      r"В первой строке $n$ и $m$ ($1 \le n \le 10^5$, $0 \le m \le 10^5$). Далее $m$ строк с $a_i \ne b_i$ — парами в ссоре.",
      r"`YES` или `NO`.", ['4 4\n1 2\n2 3\n3 4\n4 1\n', '3 3\n1 2\n2 3\n3 1\n'])
class _:
    def gen(r, lv):
        n = r.randint(1, 8) if lv < 3 else size(lv, 10 ** 5)
        if lv < 3: es = edges(r, n, r.randint(0, 8)) if n > 1 else []
        elif lv % 2:
            side = [r.randint(0, 1) for _ in range(n + 1)]; es = []
            while len(es) < n:
                a, b = r.randint(1, n), r.randint(1, n)
                if a != b and side[a] != side[b]: es.append((a, b))
        else:
            es = edges(r, n, n)
        return fmt(n, es)

    def solve(d):
        t = ints(d); n, m = t[0], t[1]; adj = [[] for _ in range(n + 1)]
        for i in range(m):
            a, b = t[2 + 2 * i], t[3 + 2 * i]; adj[a].append(b); adj[b].append(a)
        col = [-1] * (n + 1)
        for s in range(1, n + 1):
            if col[s] >= 0: continue
            col[s] = 0; q = [s]
            while q:
                v = q.pop()
                for u in adj[v]:
                    if col[u] < 0: col[u] = col[v] ^ 1; q.append(u)
                    elif col[u] == col[v]: return 'NO'
        return 'YES'

    def brute(d):
        t = ints(d); n, m = t[0], t[1]; es = [(t[2 + 2 * i], t[3 + 2 * i]) for i in range(m)]
        return 'YES' if any(all((mask >> (a - 1) & 1) != (mask >> (b - 1) & 1) for a, b in es) for mask in range(1 << n)) else 'NO'


@prob('power_lines', 'Линии электропередач', 'olympiad', ['Графы', 'Жадные'], 45,
      r"Нужно соединить линиями электропередач $n$ сёл. Известны $m$ возможных линий: между сёлами $a_i$ и $b_i$ стоимостью $c_i$. Найдите наименьшую суммарную стоимость, при которой из любого села можно добраться до любого другого, или $-1$, если это невозможно.",
      r"В первой строке $n$ и $m$ ($1 \le n \le 10^5$, $0 \le m \le 2 \cdot 10^5$). Далее $m$ строк с $a_i$, $b_i$, $c_i$ ($1 \le c_i \le 10^6$, возможны петли и повторы).",
      r"Наименьшая стоимость или $-1$.", ['4 5\n1 2 1\n2 3 2\n3 4 3\n1 4 10\n1 3 5\n', '3 1\n1 2 5\n'])
class _:
    def gen(r, lv):
        n = r.randint(1, 6) if lv < 3 else size(lv, 10 ** 5); m = r.randint(0, 9) if lv < 3 else 2 * n
        es = edges(r, n, m, wmax=10 if lv < 3 else 10 ** 6, simple=False)
        if lv >= 3 and lv % 2:  # keep it connected
            es += [(i, r.randint(1, i - 1), r.randint(1, 10 ** 6)) for i in range(2, n + 1)]
        return fmt(n, es)

    def solve(d):
        t = ints(d); n, m = t[0], t[1]; es = sorted((t[4 + 3 * i], t[2 + 3 * i], t[3 + 3 * i]) for i in range(m)); p = list(range(n + 1))
        def f(x):
            while p[x] != x: p[x] = p[p[x]]; x = p[x]
            return x
        tot = cnt = 0
        for c, a, b in es:
            a, b = f(a), f(b)
            if a != b: p[a] = b; tot += c; cnt += 1
        return str(tot if cnt == n - 1 else -1)

    def brute(d):  # Prim, O(n^2)
        t = ints(d); n, m = t[0], t[1]; INF = 10 ** 18; w = [[INF] * (n + 1) for _ in range(n + 1)]
        for i in range(m):
            a, b, c = t[2 + 3 * i:5 + 3 * i]
            if a != b: w[a][b] = w[b][a] = min(w[a][b], c)
        dist = [INF] * (n + 1); dist[1] = 0; used = [False] * (n + 1); tot = 0
        for _ in range(n):
            v = min((x for x in range(1, n + 1) if not used[x]), key=lambda x: dist[x])
            if dist[v] == INF: return '-1'
            used[v] = True; tot += dist[v]
            for u in range(1, n + 1):
                if not used[u] and w[v][u] < dist[u]: dist[u] = w[v][u]
        return str(tot)


@prob('signal_delay', 'Сигнал по горным постам', 'olympiad', ['Графы'], 46,
      r"Между $n$ постами проложены $m$ **односторонних** каналов связи: канал $a \to b$ передаёт сигнал за $c$ минут. Сигнал запускают на посту $s$. Через сколько минут он дойдёт до всех постов? Если какой-то пост недостижим, выведите $-1$.",
      r"В первой строке $n$, $m$ и $s$ ($1 \le n \le 5 \cdot 10^4$, $0 \le m \le 10^5$). Далее $m$ строк с $a_i$, $b_i$, $c_i$ ($1 \le c_i \le 10^4$).",
      r"Наибольшее время или $-1$.", ['4 3 2\n2 1 1\n2 3 1\n3 4 1\n', '3 1 1\n1 2 5\n'], time=2)
class _:
    def gen(r, lv):
        n = r.randint(1, 6) if lv < 3 else size(lv, 5 * 10 ** 4); m = r.randint(0, 9) if lv < 3 else 2 * n
        es = edges(r, n, m, True, 10 if lv < 3 else 10 ** 4)
        if lv >= 3 and lv % 2: es += [(i - 1, i, r.randint(1, 10 ** 4)) for i in range(2, n + 1)]
        s = 1 if lv % 2 else r.randint(1, n)
        return '%d %d %d\n%s' % (n, len(es), s, ''.join('%d %d %d\n' % e for e in es))

    def solve(d):
        t = ints(d); n, m, s = t[:3]; adj = [[] for _ in range(n + 1)]
        for i in range(m):
            a, b, c = t[3 + 3 * i:6 + 3 * i]; adj[a].append((b, c))
        dist = [None] * (n + 1); dist[s] = 0; pq = [(0, s)]
        while pq:
            dv, v = heapq.heappop(pq)
            if dv > dist[v]: continue
            for u, c in adj[v]:
                if dist[u] is None or dv + c < dist[u]: dist[u] = dv + c; heapq.heappush(pq, (dist[u], u))
        vals = dist[1:]
        return '-1' if None in vals else str(max(vals))

    def brute(d):
        t = ints(d); n, m, s = t[:3]; INF = float('inf'); dist = [INF] * (n + 1); dist[s] = 0
        for _ in range(n):
            for i in range(m):
                a, b, c = t[3 + 3 * i:6 + 3 * i]
                dist[b] = min(dist[b], dist[a] + c)
        mx = max(dist[1:]); return '-1' if mx == INF else str(mx)


def tree_par(r, lv, big):
    n = r.randint(1, 8) if lv < 3 else size(lv, big)
    shape = r.choice(['rand', 'path', 'deep'])
    par = [0, 0]
    for i in range(2, n + 1):
        par.append(r.randint(1, i - 1) if shape == 'rand' else (i - 1 if shape == 'path' else max(1, i - r.randint(1, 3))))
    return n, par


@prob('lineage_height', 'Высота родословной', 'training', ['Графы'], 22,
      r"Родословное дерево рода: у каждого, кроме родоначальника (номер $1$), есть отец, и номер отца меньше номера сына. Высотой называют наибольшее число поколений от родоначальника: у одного родоначальника высота $0$. Найдите высоту.",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Во второй — $n-1$ чисел $p_2, \dots, p_n$ ($1 \le p_i < i$). При $n=1$ вторая строка пустая.",
      r"Высота дерева.", ['5\n1 1 2 4\n'])
class _:
    def gen(r, lv):
        n, par = tree_par(r, lv, 10 ** 5)
        return '%d\n%s\n' % (n, nums(par[2:]))

    def solve(d):
        t = ints(d); n = t[0]; dep = [0] * (n + 1)
        for i in range(2, n + 1): dep[i] = dep[t[i - 1]] + 1
        return str(max(dep))

    def brute(d):
        t = ints(d); n = t[0]; best = 0
        for v in range(1, n + 1):
            c = 0
            while v != 1: v = t[v - 1]; c += 1
            best = max(best, c)
        return str(best)


@prob('far_camps', 'Самые далёкие стоянки', 'training', ['Графы'], 40,
      r"Сети стоянок в горах образуют дерево: $n$ стоянок и $n-1$ тропа, от любой можно дойти до любой единственным путём. Найдите наибольшее число троп на пути между двумя стоянками.",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Далее $n-1$ строк с парами $a_i$, $b_i$.",
      r"Длина самого длинного пути.", ['5\n1 2\n1 3\n3 4\n3 5\n'])
class _:
    def gen(r, lv):
        n = r.randint(1, 8) if lv < 3 else size(lv, 10 ** 5); shape = r.choice(['rand', 'path', 'star'])
        perm = list(range(1, n + 1)); r.shuffle(perm); es = []
        for i in range(2, n + 1):
            p = r.randint(1, i - 1) if shape == 'rand' else (i - 1 if shape == 'path' else 1)
            es.append((perm[p - 1], perm[i - 1]))
        return '%d\n%s' % (n, ''.join('%d %d\n' % e for e in es))

    def solve(d):
        t = ints(d); n = t[0]; adj = [[] for _ in range(n + 1)]
        for i in range(n - 1): a, b = t[1 + 2 * i], t[2 + 2 * i]; adj[a].append(b); adj[b].append(a)
        def far(s):
            dist = {s: 0}; q = deque([s]); last = s
            while q:
                v = q.popleft(); last = v
                for u in adj[v]:
                    if u not in dist: dist[u] = dist[v] + 1; q.append(u)
            return last, dist[last]
        return str(far(far(1)[0])[1])

    def brute(d):
        t = ints(d); n = t[0]; adj = [[] for _ in range(n + 1)]
        for i in range(n - 1): a, b = t[1 + 2 * i], t[2 + 2 * i]; adj[a].append(b); adj[b].append(a)
        best = 0
        for s in range(1, n + 1):
            dist = {s: 0}; st = [s]
            while st:
                v = st.pop()
                for u in adj[v]:
                    if u not in dist: dist[u] = dist[v] + 1; st.append(u)
            best = max(best, max(dist.values()))
        return str(best)


@prob('common_ancestor', 'Общий предок рода', 'olympiad', ['Графы', 'Структуры данных'], 50,
      r"Дано родословное дерево: у каждого, кроме родоначальника (номер $1$), есть отец, причём номер отца меньше номера сына. Для $q$ запросов найдите **наименьшего общего предка** двух людей (предком считается и сам человек).",
      r"В первой строке $n$ и $q$ ($1 \le n, q \le 10^5$). Во второй — $p_2, \dots, p_n$ ($1 \le p_i < i$). Далее $q$ строк с $u_j$, $v_j$.",
      r"Для каждого запроса — номер общего предка, по одному в строке.", ['5 2\n1 1 2 2\n4 5\n4 3\n'])
class _:
    def gen(r, lv):
        n, par = tree_par(r, lv, 10 ** 5); q = size(lv, 10 ** 5)
        return '%d %d\n%s\n%s' % (n, q, nums(par[2:]), ''.join('%d %d\n' % (r.randint(1, n), r.randint(1, n)) for _ in range(q)))

    def solve(d):
        t = ints(d); n, q = t[0], t[1]; par = [0, 0] + t[2:n + 1]; L = max(1, n.bit_length())
        up = [[0] * (n + 1) for _ in range(L)]; dep = [0] * (n + 1)
        for i in range(2, n + 1): up[0][i] = par[i]; dep[i] = dep[par[i]] + 1
        up[0][1] = 1
        for k in range(1, L):
            for i in range(1, n + 1): up[k][i] = up[k - 1][up[k - 1][i]]
        out = []
        for j in range(q):
            u, v = t[n + 1 + 2 * j], t[n + 2 + 2 * j]
            if dep[u] < dep[v]: u, v = v, u
            diff = dep[u] - dep[v]
            for k in range(L):
                if diff >> k & 1: u = up[k][u]
            if u != v:
                for k in range(L - 1, -1, -1):
                    if up[k][u] != up[k][v]: u, v = up[k][u], up[k][v]
                u = up[0][u]
            out.append(str(u))
        return '\n'.join(out)

    def brute(d):
        t = ints(d); n, q = t[0], t[1]; par = [0, 0] + t[2:n + 1]; out = []
        for j in range(q):
            u, v = t[n + 1 + 2 * j], t[n + 2 + 2 * j]; anc = set()
            while True:
                anc.add(u)
                if u == 1: break
                u = par[u]
            while v not in anc: v = par[v]
            out.append(str(v))
        return '\n'.join(out)


@prob('knight_ride', 'Ход коня в кок-бору', 'training', ['Графы'], 34,
      r"На доске $n \times n$ стоит шахматный конь (ход буквой «Г»: на 2 клетки по одной оси и на 1 по другой). За какое наименьшее число ходов он дойдёт из клетки $(x_1, y_1)$ в $(x_2, y_2)$? Если это невозможно, выведите $-1$.",
      r"В первой строке $n$ ($1 \le n \le 1000$). Во второй — $x_1, y_1, x_2, y_2$ ($1 \le x_i, y_i \le n$).",
      r"Число ходов или $-1$.", ['8\n1 1 8 8\n', '3\n1 1 2 2\n'])
class _:
    def gen(r, lv):
        n = r.randint(1, 6) if lv < 3 else size(lv, 1000)
        return '%d\n%d %d %d %d\n' % (n, r.randint(1, n), r.randint(1, n), r.randint(1, n), r.randint(1, n))

    def solve(d):
        n, x1, y1, x2, y2 = ints(d)[:5]; dist = {(x1, y1): 0}; q = deque([(x1, y1)])
        while q:
            x, y = q.popleft()
            if (x, y) == (x2, y2): return str(dist[(x, y)])
            for dx, dy in ((1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)):
                a, b = x + dx, y + dy
                if 1 <= a <= n and 1 <= b <= n and (a, b) not in dist: dist[(a, b)] = dist[(x, y)] + 1; q.append((a, b))
        return '-1'

    def brute(d):
        n, x1, y1, x2, y2 = ints(d)[:5]; INF = 10 ** 9; f = {(i, j): INF for i in range(1, n + 1) for j in range(1, n + 1)}; f[(x1, y1)] = 0; ch = True
        while ch:
            ch = False
            for (x, y), v in list(f.items()):
                for dx, dy in ((1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)):
                    k = (x + dx, y + dy)
                    if k in f and f[k] + 1 < v: f[(x, y)] = v = f[k] + 1; ch = True
        return str(f[(x2, y2)] if f[(x2, y2)] < INF else -1)


@prob('guards_pass', 'Охрана перевала', 'training', ['Комбинаторика'], 42,
      r"На перевале — шахматная доска $n \times n$. Нужно расставить $n$ охранников так, чтобы никакие двое не стояли на одной горизонтали, вертикали или диагонали. Сколько существует расстановок?",
      r"Одно число $n$ ($1 \le n \le 10$).",
      r"Количество расстановок.", ['4\n', '1\n'])
class _:
    def gen(r, lv):
        return '%d\n' % (lv % 3 + 1 if lv < 3 else lv + 1)

    def solve(d):
        n = int(d.split()[0]); full = (1 << n) - 1
        def go(cols, d1, d2):
            if cols == full: return 1
            res = 0; free = full & ~(cols | d1 | d2)
            while free:
                b = free & -free; free ^= b
                res += go(cols | b, ((d1 | b) << 1) & full, (d2 | b) >> 1)
            return res
        return str(go(0, 0, 0))

    def brute(d):
        n = int(d.split()[0]); cnt = 0
        for p in itertools.permutations(range(n)):
            if len({i + p[i] for i in range(n)}) == n and len({i - p[i] for i in range(n)}) == n: cnt += 1
        return str(cnt)


@prob('kth_order', 'Порядок в очереди джигитов', 'training', ['Комбинаторика', 'Математика'], 40,
      r"Выпишем в лексикографическом порядке все перестановки чисел от $1$ до $n$. Найдите $k$-ю по счёту.",
      r"В первой строке $n$ и $k$ ($1 \le n \le 20$, $1 \le k \le n!$).",
      r"$n$ чисел через пробел.", ['3 3\n', '4 1\n'])
class _:
    def gen(r, lv):
        n = r.randint(1, 5) if lv < 3 else r.randint(10, 20); return '%d %d\n' % (n, r.randint(1, math.factorial(n)))

    def solve(d):
        n, k = ints(d)[:2]; k -= 1; pool = list(range(1, n + 1)); res = []
        for i in range(n, 0, -1):
            f = math.factorial(i - 1); res.append(pool.pop(k // f)); k %= f
        return nums(res)

    def brute(d):
        n, k = ints(d)[:2]
        return nums(next(itertools.islice(itertools.permutations(range(1, n + 1)), k - 1, None)))


@prob('gift_subsets', 'Наборы подарков', 'olympiad', ['DP', 'Комбинаторика'], 44,
      r"Есть $n$ подарков стоимостью $a_i$. Сколько существует наборов (подмножеств по номерам, включая пустое), суммарная стоимость которых равна $S$? Ответ по модулю $10^9+7$.",
      r"В первой строке $n$ и $S$ ($1 \le n \le 100$, $0 \le S \le 5000$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 100$).",
      r"Количество подмножеств по модулю $10^9+7$.", ['3 4\n1 3 1\n', '2 0\n0 0\n'])
class _:
    def gen(r, lv):
        n = r.randint(1, 8) if lv < 3 else size(lv, 100); hi = 5 if lv < 3 else 100
        a = [r.randint(0, hi) for _ in range(n)]
        return '%d %d\n%s\n' % (n, r.randint(0, 12) if lv < 3 else r.randint(0, min(5000, sum(a))), nums(a))

    def solve(d):
        t = ints(d); n, s = t[0], t[1]; f = [1] + [0] * s
        for x in t[2:2 + n]:
            for v in range(s, x - 1, -1): f[v] = (f[v] + f[v - x]) % MOD
        return str(f[s])

    def brute(d):
        t = ints(d); n, s = t[0], t[1]; a = t[2:2 + n]
        return str(sum(1 for m in range(1 << n) if sum(a[i] for i in range(n) if m >> i & 1) == s) % MOD)


@prob('nooruz_numbers', 'Счастливые числа Нооруз', 'training', ['Математика', 'DP'], 38,
      r"Число называется счастливым, если у него нет простых делителей, кроме $2$, $3$ и $5$ (число $1$ тоже счастливое). Найдите $n$-е по возрастанию счастливое число.",
      r"Одно число $n$ ($1 \le n \le 10^5$).",
      r"$n$-е счастливое число.", ['10\n', '1\n'])
class _:
    def gen(r, lv):
        return '%d\n' % (r.randint(1, 30) if lv < 3 else [10 ** 3, 5000, 10 ** 4, 3 * 10 ** 4, 6 * 10 ** 4, 10 ** 5, 99999][min(6, lv - 3)] - r.randint(0, 9))

    def solve(d):
        n = int(d.split()[0]); u = [1]; i2 = i3 = i5 = 0
        while len(u) < n:
            nx = min(u[i2] * 2, u[i3] * 3, u[i5] * 5); u.append(nx)
            if nx == u[i2] * 2: i2 += 1
            if nx == u[i3] * 3: i3 += 1
            if nx == u[i5] * 5: i5 += 1
        return str(u[n - 1])

    def brute(d):
        n = int(d.split()[0]); c = 0; x = 0
        while c < n:
            x += 1; y = x
            for p in (2, 3, 5):
                while y % p == 0: y //= p
            if y == 1: c += 1
        return str(x)


@prob('road_primes', 'Простые на дороге', 'training', ['Теория чисел'], 30,
      r"Вдоль дороги стоят столбы с номерами от $1$ до $n$. Сколько номеров простые числа?",
      r"Одно число $n$ ($1 \le n \le 3 \cdot 10^6$).",
      r"Количество простых чисел от $1$ до $n$.", ['10\n', '1\n'])
class _:
    def gen(r, lv):
        return '%d\n' % (r.randint(1, 60) if lv < 3 else [10 ** 4, 10 ** 5, 5 * 10 ** 5, 10 ** 6, 2 * 10 ** 6, 3 * 10 ** 6, 2999999][min(6, lv - 3)] - r.randint(0, 99))

    def solve(d):
        n = int(d.split()[0])
        if n < 2: return '0'
        s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
        for i in range(2, int(n ** 0.5) + 1):
            if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
        return str(sum(s))

    def brute(d):
        n = int(d.split()[0])
        return str(sum(1 for x in range(2, n + 1) if all(x % y for y in range(2, int(x ** 0.5) + 1))))


@prob('tandyr_power', 'Тандыр и степени', 'training', ['Теория чисел', 'Математика'], 32,
      r"Найдите $a^b \bmod m$.",
      r"В единственной строке числа $a$, $b$, $m$ ($0 \le a \le 10^{18}$, $0 \le b \le 10^{18}$, $1 \le m \le 10^9$). Считайте $0^0 = 1$.",
      r"Остаток от деления $a^b$ на $m$.", ['2 10 1000\n', '5 0 1\n'])
class _:
    def gen(r, lv):
        if lv < 3: return '%d %d %d\n' % (r.randint(0, 9), r.randint(0, 12), r.randint(1, 50))
        return '%d %d %d\n' % (r.randint(0, 10 ** 18), r.randint(0, 10 ** 18), r.randint(1, 10 ** 9))

    def solve(d):
        a, b, m = ints(d)[:3]; res = 1 % m; a %= m
        while b:
            if b & 1: res = res * a % m
            a = a * a % m; b >>= 1
        return str(res)

    def brute(d):
        a, b, m = ints(d)[:3]; res = 1 % m
        for _ in range(b): res = res * a % m
        return str(res)


@prob('flock_gcd', 'НОД и НОК отары', 'training', ['Теория чисел'], 26,
      r"Даны размеры $n$ отар. Найдите наибольший общий делитель всех чисел и их наименьшее общее кратное по модулю $10^9+7$.",
      r"В первой строке $n$ ($1 \le n \le 10^5$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^6$).",
      r"Два числа: НОД и НОК по модулю $10^9+7$.", ['3\n4 6 8\n'])
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); hi = 20 if lv < 3 else 10 ** 6; k = r.choice([1, 2, 6, 12])
        return '%d\n%s\n' % (n, nums([k * r.randint(1, max(1, hi // k)) for _ in range(n)]))

    def solve(d):
        t = ints(d); a = t[1:1 + t[0]]; g = 0
        for x in a: g = math.gcd(g, x)
        e = {}
        for x in a:
            p = 2
            while p * p <= x:
                c = 0
                while x % p == 0: x //= p; c += 1
                if c: e[p] = max(e.get(p, 0), c)
                p += 1
            if x > 1: e[x] = max(e.get(x, 0), 1)
        l = 1
        for p, c in e.items(): l = l * pow(p, c, MOD) % MOD
        return '%d %d' % (g, l)

    def brute(d):
        t = ints(d); a = t[1:1 + t[0]]; g = 0; l = 1
        for x in a: g = math.gcd(g, x); l = l * x // math.gcd(l, x)
        return '%d %d' % (g, l % MOD)


@prob('ones_total', 'Единицы в номерах', 'olympiad', ['Математика'], 48,
      r"Запишем числа от $1$ до $n$ в двоичной системе. Сколько всего цифр `1` будет в этих записях?",
      r"Одно число $n$ ($1 \le n \le 10^{18}$).",
      r"Общее число единиц.", ['5\n', '1\n'])
class _:
    def gen(r, lv):
        return '%d\n' % (r.randint(1, 40) if lv < 3 else r.randint(10 ** (lv * 2 - 3), 10 ** (min(18, lv * 2 - 2))))

    def solve(d):
        n = int(d.split()[0]) + 1; res = 0; b = 0
        while (1 << b) <= n:
            period = 1 << (b + 1); res += (n // period) * (1 << b) + max(0, n % period - (1 << b)); b += 1
        return str(res)

    def brute(d):
        n = int(d.split()[0]); return str(sum(bin(x).count('1') for x in range(1, n + 1)))


@prob('pass_game', 'Игра на перевале', 'olympiad', ['Теория игр', 'DP'], 46,
      r"На перевале лежат $n$ камней. Игроки ходят по очереди, начинает первый. За ход можно взять любое количество камней из заданного набора $m_1, \dots, m_k$ (если в куче достаточно камней). Кто не может сделать ход, проигрывает. Оба играют наилучшим образом. Выиграет ли первый?",
      r"В первой строке $n$ и $k$ ($1 \le n \le 10^6$, $1 \le k \le 5$). Во второй — $k$ различных чисел $m_i$ ($1 \le m_i \le 100$).",
      r"`WIN`, если выигрывает первый, иначе `LOSE`.", ['10 3\n1 3 4\n', '5 1\n5\n'], time=2)
class _:
    def gen(r, lv):
        k = r.randint(1, 3 if lv < 3 else 5); m = r.sample(range(1, 8 if lv < 3 else 100), k)
        return '%d %d\n%s\n' % (r.randint(1, 20) if lv < 3 else size(lv, 10 ** 6), k, nums(m))

    def solve(d):
        t = ints(d); n, k = t[0], t[1]; m = t[2:2 + k]; win = bytearray(n + 1)
        for v in range(1, n + 1):
            for x in m:
                if x <= v and not win[v - x]: win[v] = 1; break
        return 'WIN' if win[n] else 'LOSE'

    def brute(d):
        t = ints(d); n, k = t[0], t[1]; m = t[2:2 + k]
        @lru_cache(None)
        def w(v): return any(x <= v and not w(v - x) for x in m)
        import sys; sys.setrecursionlimit(5000)
        return 'WIN' if w(n) else 'LOSE'


@prob('harvest_fenwick', 'Урожай по участкам', 'olympiad', ['Структуры данных'], 48,
      r"Поле разбито на $n$ участков, на $i$-м собрано $a_i$ центнеров. Поступают $q$ запросов: добавить урожай на участок или узнать суммарный урожай на отрезке участков.",
      r"В первой строке $n$ и $q$ ($1 \le n, q \le 10^5$). Во второй — $a_i$ ($0 \le a_i \le 10^9$). Далее $q$ строк: `1 i x` — прибавить $x$ к участку $i$ ($0 \le x \le 10^9$); `2 l r` — узнать сумму на участках от $l$ до $r$ ($1 \le l \le r \le n$).",
      r"На каждый запрос второго типа — сумма, по одной в строке.", ['5 3\n1 2 3 4 5\n2 2 4\n1 3 10\n2 1 5\n'], time=2)
class _:
    def gen(r, lv):
        n = size(lv, 10 ** 5); q = size(lv, 10 ** 5); hi = 5 if lv < 3 else 10 ** 9
        a = [r.randint(0, hi) for _ in range(n)]; ops = []
        for _ in range(q):
            if r.random() < 0.5: ops.append('1 %d %d' % (r.randint(1, n), r.randint(0, hi)))
            else:
                l = r.randint(1, n); ops.append('2 %d %d' % (l, r.randint(l, n)))
        ops.append('2 1 %d' % n)
        return '%d %d\n%s\n%s\n' % (n, q + 1, nums(a), '\n'.join(ops))

    def solve(d):
        t = ints(d); n, q = t[0], t[1]; tree = [0] * (n + 1)
        def add(i, x):
            while i <= n: tree[i] += x; i += i & -i
        def pre(i):
            s = 0
            while i: s += tree[i]; i -= i & -i
            return s
        for i, x in enumerate(t[2:2 + n], 1): add(i, x)
        out = []; p = 2 + n
        for _ in range(q):
            k, x, y = t[p:p + 3]; p += 3
            if k == 1: add(x, y)
            else: out.append(str(pre(y) - pre(x - 1)))
        return '\n'.join(out)

    def brute(d):
        t = ints(d); n, q = t[0], t[1]; a = t[2:2 + n]; out = []; p = 2 + n
        for _ in range(q):
            k, x, y = t[p:p + 3]; p += 3
            if k == 1: a[x - 1] += y
            else: out.append(str(sum(a[x - 1:y])))
        return '\n'.join(out)


@prob('shared_plot', 'Общий участок', 'training', ['Геометрия'], 14,
      r"Два прямоугольных участка со сторонами, параллельными осям, заданы координатами левого нижнего и правого верхнего углов. Найдите площадь их общей части (если участки только касаются, она равна $0$).",
      r"В двух строках по четыре числа $x_1, y_1, x_2, y_2$ ($x_1 < x_2$, $y_1 < y_2$, $|x|, |y| \le 10^9$).",
      r"Площадь общей части.", ['0 0 4 4\n2 2 6 6\n', '0 0 1 1\n1 1 2 2\n'])
class _:
    def gen(r, lv):
        h = 6 if lv < 3 else 10 ** 9
        def rect():
            x = r.randint(-h, h - 1); y = r.randint(-h, h - 1)
            return x, y, r.randint(x + 1, min(h, x + (h if lv > 3 else 4))), r.randint(y + 1, min(h, y + (h if lv > 3 else 4)))
        return '%d %d %d %d\n%d %d %d %d\n' % (rect() + rect())

    def solve(d):
        a = ints(d); w = min(a[2], a[6]) - max(a[0], a[4]); h = min(a[3], a[7]) - max(a[1], a[5])
        return str(w * h if w > 0 and h > 0 else 0)

    def brute(d):
        a = ints(d); c = 0
        for x in range(-8, 9):
            for y in range(-8, 9):
                if a[0] <= x < a[2] and a[1] <= y < a[3] and a[4] <= x < a[6] and a[5] <= y < a[7]: c += 1
        return str(c)


@prob('stick_triangles', 'Палки для юрты', 'olympiad', ['Сортировка', 'Двоичный поиск'], 44,
      r"Есть $n$ палок длиной $a_i$. Сколько существует троек палок (по номерам, порядок в тройке не важен), из которых можно составить невырожденный треугольник?",
      r"В первой строке $n$ ($3 \le n \le 2000$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"Количество троек.", ['4\n2 2 3 4\n'], time=1)
class _:
    def gen(r, lv):
        n = max(3, size(lv, 2000)); hi = 8 if lv < 3 else r.choice([50, 10 ** 9])
        return '%d\n%s\n' % (n, nums([r.randint(1, hi) for _ in range(n)]))

    def solve(d):
        t = ints(d); n = t[0]; a = sorted(t[1:1 + n]); cnt = 0
        for k in range(2, n):
            i, j = 0, k - 1
            while i < j:
                if a[i] + a[j] > a[k]: cnt += j - i; j -= 1
                else: i += 1
        return str(cnt)

    def brute(d):
        t = ints(d); n = t[0]; a = t[1:1 + n]
        return str(sum(1 for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n)
                       if a[i] + a[j] > a[k] and a[i] + a[k] > a[j] and a[j] + a[k] > a[i]))
