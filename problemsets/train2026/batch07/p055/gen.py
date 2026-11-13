# -*- coding: utf-8 -*-
import sys, random, heapq, itertools
from collections import deque, defaultdict


def ints(s):
    return list(map(int, s.split()))


def sz(r, k, big, lo=2, tiny=7):
    """size of test k (1..10); k == 0 means a tiny random test for brute force checking"""
    if k == 0:
        return r.randint(lo, max(lo, tiny))
    return max(lo, [4, 6, 10, big // 1000, big // 200, big // 50, big // 10, big // 4, big // 2, big][k - 1])


def tree(r, n, k=0):
    """edges (u, v) of a random tree on 1..n, labels shuffled; shape depends on k"""
    s = k % 5
    e = []
    for i in range(2, n + 1):
        if s == 0:
            p = r.randint(1, i - 1)
        elif s == 1:
            p = i - 1
        elif s == 2:
            p = 1
        elif s == 3:
            p = max(1, i - r.randint(1, 3))
        else:
            p = r.randint(max(1, i // 2), i - 1)
        e.append((p, i))
    perm = list(range(1, n + 1))
    r.shuffle(perm)
    e = [(perm[a - 1], perm[b - 1]) if r.random() < .5 else (perm[b - 1], perm[a - 1]) for a, b in e]
    r.shuffle(e)
    return e


def graph(r, n, m, conn=False, k=0):
    """simple undirected graph, about m edges (clipped to the maximum), as a list of (u, v)"""
    mx = n * (n - 1) // 2
    m = min(m, mx)
    es = set()
    if conn:
        for a, b in tree(r, n, k):
            es.add((min(a, b), max(a, b)))
        m = max(m, n - 1)
    if m > mx // 2 and mx <= 2000000:
        allp = [(a, b) for a in range(1, n + 1) for b in range(a + 1, n + 1) if (a, b) not in es]
        r.shuffle(allp)
        es.update(allp[:m - len(es)])
    else:
        while len(es) < m:
            a, b = r.randint(1, n), r.randint(1, n)
            if a != b:
                es.add((min(a, b), max(a, b)))
    L = [(a, b) if r.random() < .5 else (b, a) for a, b in es]
    r.shuffle(L)
    return L


def digraph(r, n, m):
    """simple directed graph (no loops, no repeated arcs), m arcs"""
    m = min(m, n * (n - 1))
    es = set()
    while len(es) < m:
        a, b = r.randint(1, n), r.randint(1, n)
        if a != b:
            es.add((a, b))
    L = list(es)
    r.shuffle(L)
    return L


def dag(r, n, m):
    """acyclic digraph with hidden random topological order, m arcs"""
    m = min(m, n * (n - 1) // 2)
    perm = list(range(1, n + 1))
    r.shuffle(perm)
    es = set()
    while len(es) < m:
        a, b = r.randint(0, n - 1), r.randint(0, n - 1)
        if a < b:
            es.add((perm[a], perm[b]))
    L = list(es)
    r.shuffle(L)
    return L


def grid(r, h, w, p=0.3, ch='#.'):
    return [''.join(ch[0] if r.random() < p else ch[1] for _ in range(w)) for _ in range(h)]


def adj(n, es, directed=False):
    g = [[] for _ in range(n + 1)]
    for e in es:
        a, b = e[0], e[1]
        g[a].append(b if len(e) == 2 else (b,) + tuple(e[2:]))
        if not directed:
            g[b].append(a if len(e) == 2 else (a,) + tuple(e[2:]))
    return g


def lines(*a):
    return "\n".join(str(x) for x in a)


def el(es):
    return "\n".join(" ".join(map(str, e)) for e in es)


class DSU:
    def __init__(self, n):
        self.p = list(range(n + 1))

    def f(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def u(self, a, b):
        a, b = self.f(a), self.f(b)
        if a == b:
            return False
        self.p[a] = b
        return True


INF = float('inf')


def hw(r, k, big, tiny=25):
    cells = sz(r, k, big, lo=1, tiny=tiny)
    h = max(1, min(cells, int(cells ** 0.5 * r.uniform(0.5, 1.5))))
    return h, max(1, cells // h)


def comps_bf(n, es):
    """components by repeated label propagation: list of label per vertex (1-indexed, index 0 unused)"""
    lab = list(range(n + 1))
    ch = True
    while ch:
        ch = False
        for a, b in es:
            m = min(lab[a], lab[b])
            if lab[a] != m or lab[b] != m:
                lab[a] = lab[b] = m
                ch = True
    return lab


def grid_labels(g, c0='#'):
    """label propagation on '#' cells (4-neighbours); returns dict cell->label"""
    h, w = len(g), len(g[0])
    lab = {(i, j): i * w + j for i in range(h) for j in range(w) if g[i][j] == c0}
    ch = True
    while ch:
        ch = False
        for (i, j) in lab:
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                c = (i + di, j + dj)
                if c in lab and lab[c] < lab[(i, j)]:
                    lab[(i, j)] = lab[c]
                    ch = True
    return lab


def rg(s):
    L = s.split('\n')
    h, w = map(int, L[0].split())
    return h, w, L[1:1 + h]


D4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
D8 = tuple((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b)


def setc(g, i, j, c):
    g[i] = g[i][:j] + c + g[i][j + 1:]


def dag_or_cyc(r, n, m, k, p=0.4):
    """DAG, and with probability p one arc is reversed-and-added so that a cycle appears"""
    es = dag(r, n, m)
    if es and r.random() < p:
        a, b = r.choice(es)
        es.append((b, a))
        r.shuffle(es)
    return es


def bip_edges(r, n, m):
    """edges between two random sides (about m of them)"""
    side = [r.randint(0, 1) for _ in range(n + 1)]
    A = [i for i in range(1, n + 1) if side[i]]
    B = [i for i in range(1, n + 1) if not side[i]]
    if not A or not B:
        return []
    m = min(m, len(A) * len(B))
    es = set()
    while len(es) < m:
        a, b = r.choice(A), r.choice(B)
        es.add((min(a, b), max(a, b)))
    es = list(es)
    r.shuffle(es)
    return es


def layered(r, n, w=2):
    """vertex 1, then layers of up to w vertices fully connected to the next layer, last vertex n; vertices shuffled except 1 and n"""
    mid = list(range(2, n))
    r.shuffle(mid)
    layers = [[1]]
    i = 0
    while i < len(mid):
        c = r.randint(1, w)
        layers.append(mid[i:i + c])
        i += c
    layers.append([n])
    es = []
    for a, b in zip(layers, layers[1:]):
        for x in a:
            for y in b:
                if r.random() < .85 or len(a) * len(b) == 1:
                    es.append((x, y))
    # make sure every vertex of a layer has a link both ways
    es = list(set(es))
    r.shuffle(es)
    return es


def dijk(n, g, s):
    d = [INF] * (n + 1)
    d[s] = 0
    pq = [(0, s)]
    while pq:
        dd, x = heapq.heappop(pq)
        if dd > d[x]:
            continue
        for y, w in g[x]:
            if dd + w < d[y]:
                d[y] = dd + w
                heapq.heappush(pq, (dd + w, y))
    return d


def floyd(n, es, directed=False):
    D = [[INF] * (n + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        D[i][i] = 0
    for a, b, w in es:
        D[a][b] = min(D[a][b], w)
        if not directed:
            D[b][a] = min(D[b][a], w)
    for x in range(1, n + 1):
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if D[i][x] + D[x][j] < D[i][j]:
                    D[i][j] = D[i][x] + D[x][j]
    return D


def lowlink(n, es):
    """returns (list of bridge edge indices, set of articulation points) for a simple undirected graph"""
    g = [[] for _ in range(n + 1)]
    for i, (a, b) in enumerate(es):
        g[a].append((b, i))
        g[b].append((a, i))
    tin = [0] * (n + 1)
    low = [0] * (n + 1)
    pe = [-1] * (n + 1)
    pos = [0] * (n + 1)
    T = 0
    bridges = []
    art = set()
    for root in range(1, n + 1):
        if tin[root]:
            continue
        T += 1
        tin[root] = low[root] = T
        stack = [root]
        rootch = 0
        while stack:
            x = stack[-1]
            if pos[x] < len(g[x]):
                y, i = g[x][pos[x]]
                pos[x] += 1
                if i == pe[x]:
                    continue
                if tin[y]:
                    low[x] = min(low[x], tin[y])
                else:
                    pe[y] = i
                    T += 1
                    tin[y] = low[y] = T
                    stack.append(y)
            else:
                stack.pop()
                if stack:
                    p = stack[-1]
                    low[p] = min(low[p], low[x])
                    if low[x] > tin[p]:
                        bridges.append(pe[x])
                    if low[x] >= tin[p]:
                        if p != root:
                            art.add(p)
                        else:
                            rootch += 1
        if rootch >= 2:
            art.add(root)
    return bridges, art


def scc(n, es):
    """Kosaraju, iterative; returns (comp ids 1..c per vertex (index 0 unused), c)"""
    g = [[] for _ in range(n + 1)]
    rg_ = [[] for _ in range(n + 1)]
    for a, b in es:
        g[a].append(b)
        rg_[b].append(a)
    seen = [False] * (n + 1)
    order = []
    for s in range(1, n + 1):
        if seen[s]:
            continue
        seen[s] = True
        st = [(s, 0)]
        while st:
            x, i = st.pop()
            if i < len(g[x]):
                st.append((x, i + 1))
                y = g[x][i]
                if not seen[y]:
                    seen[y] = True
                    st.append((y, 0))
            else:
                order.append(x)
    comp = [0] * (n + 1)
    c = 0
    for s in reversed(order):
        if comp[s]:
            continue
        c += 1
        comp[s] = c
        st = [s]
        while st:
            x = st.pop()
            for y in rg_[x]:
                if not comp[y]:
                    comp[y] = c
                    st.append(y)
    return comp, c


def is_connected(n, es, skip_vertex=0):
    vs = [i for i in range(1, n + 1) if i != skip_vertex]
    if not vs:
        return True
    g = adj(n, [e for e in es if skip_vertex not in e[:2]])
    seen = {vs[0]}
    st = [vs[0]]
    while st:
        x = st.pop()
        for y in g[x]:
            y = y if isinstance(y, int) else y[0]
            if y not in seen:
                seen.add(y)
                st.append(y)
    return len(seen) == len(vs)

def gen(r, k):
    n = sz(r, k, 100000, lo=1)
    if k % 2:
        es = bip_edges(r, n, r.randint(n // 2, n))
    else:
        es = graph(r, n, r.randint(n // 2, int(1.5 * n)))
    return '%d %d\n' % (n, len(es)) + el(es)

def sol(s):
    v = ints(s); n, m = v[0], v[1]
    g = adj(n, [(v[2 + 2 * i], v[3 + 2 * i]) for i in range(m)])
    d = [[-1, -1] for _ in range(n + 1)]; d[1][0] = 0; q = deque([(1, 0)])
    while q:
        x, p = q.popleft()
        for y in g[x]:
            if d[y][p ^ 1] < 0:
                d[y][p ^ 1] = d[x][p] + 1; q.append((y, p ^ 1))
    return '%d %d' % (sum(1 for i in range(1, n + 1) if d[i][0] >= 0), sum(1 for i in range(1, n + 1) if d[i][1] >= 0))

def brute(s):
    v = ints(s); n, m = v[0], v[1]; es = [(v[2 + 2 * i], v[3 + 2 * i]) for i in range(m)]
    cur = {1}; ev = {1}; od = set()
    for t in range(1, 3 * n + 2):
        cur = {y for x in cur for a, b in es for y in ((b,) if a == x else (a,) if b == x else ())}
        (od if t % 2 else ev).update(cur)
    return '%d %d' % (len(ev), len(od))

if __name__ == "__main__":
    k = int(sys.argv[1])
    print(gen(random.Random(55 * 1000 + k), k))
