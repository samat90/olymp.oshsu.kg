import sys, random, bisect, math
from collections import deque, defaultdict
MOD = 10**9 + 7


def sz(r, lv, tiny, big):
    if lv < 0:
        return r.randint(1, tiny)
    return max(1, int(tiny * (big / tiny) ** (lv / 9)))


def rtree(r, n, kind=None):
    kind = kind or r.choice(['rand', 'rand', 'path', 'star', 'deep', 'bin', 'cat'])
    par = [0] * (n + 1)
    for i in range(2, n + 1):
        if kind == 'path': p = i - 1
        elif kind == 'star': p = 1
        elif kind == 'deep': p = r.randint(max(1, i - 3), i - 1)
        elif kind == 'bin': p = i // 2
        elif kind == 'cat': p = i - 1 if i % 2 == 0 else max(1, i - 2)
        else: p = r.randint(1, i - 1)
        par[i] = p
    perm = list(range(2, n + 1)); r.shuffle(perm); perm = [0, 1] + perm
    ed = []
    for i in range(2, n + 1):
        a, b = perm[par[i]], perm[i]
        if r.random() < 0.5: a, b = b, a
        ed.append((a, b))
    r.shuffle(ed)
    return ed


def tree_text(ed):
    return "\n".join("%d %d" % (a, b) for a, b in ed)


def read_edges(it, n):
    adj = [[] for _ in range(n + 1)]
    for _ in range(n - 1):
        a = int(next(it)); b = int(next(it))
        adj[a].append(b); adj[b].append(a)
    return adj


def root_tree(n, adj, root=1):
    par = [0] * (n + 1); dep = [0] * (n + 1); order = [root]
    seen = [False] * (n + 1); seen[root] = True
    for v in order:
        for u in adj[v]:
            if not seen[u]:
                seen[u] = True; par[u] = v; dep[u] = dep[v] + 1; order.append(u)
    return par, dep, order


def pre_order(n, adj, root=1):
    par = [0] * (n + 1); out = []; st = [root]; seen = [False] * (n + 1); seen[root] = True
    while st:
        v = st.pop(); out.append(v)
        for u in adj[v]:
            if not seen[u]:
                seen[u] = True; par[u] = v; st.append(u)
    return par, out


def bfs_dist(n, adj, s):
    d = [-1] * (n + 1); d[s] = 0; q = deque([s])
    while q:
        v = q.popleft()
        for u in adj[v]:
            if d[u] < 0:
                d[u] = d[v] + 1; q.append(u)
    return d


class LCA:
    def __init__(s, n, par, dep, root=1):
        s.dep = dep
        up0 = par[:]; up0[root] = root; up0[0] = 0
        s.up = [up0]
        for _ in range(max(1, n.bit_length())):
            pv = s.up[-1]
            s.up.append([pv[pv[v]] for v in range(n + 1)])

    def kth(s, v, k):
        j = 0
        while k and v:
            if k & 1: v = s.up[j][v]
            k >>= 1; j += 1
            if j >= len(s.up): break
        return v

    def lca(s, a, b):
        if s.dep[a] < s.dep[b]: a, b = b, a
        a = s.kth(a, s.dep[a] - s.dep[b])
        if a == b: return a
        for j in range(len(s.up) - 1, -1, -1):
            if s.up[j][a] != s.up[j][b]:
                a = s.up[j][a]; b = s.up[j][b]
        return s.up[0][a]

    def dist(s, a, b):
        return s.dep[a] + s.dep[b] - 2 * s.dep[s.lca(a, b)]


def rbin(r, n, p=None):
    p = r.choice([0, 0, 0.5, 0.85, 1.0]) if p is None else p
    Lc = [0] * (n + 1); Rc = [0] * (n + 1)
    slots = []
    def add(i):
        s = [(i, 0), (i, 1)]
        if r.random() < 0.5: s.reverse()
        slots.extend(s)
    add(1)
    for i in range(2, n + 1):
        idx = len(slots) - 1 if r.random() < p else r.randrange(len(slots))
        slots[idx], slots[-1] = slots[-1], slots[idx]
        v, side = slots.pop()
        if side == 0: Lc[v] = i
        else: Rc[v] = i
        add(i)
    perm = list(range(2, n + 1)); r.shuffle(perm); perm = [0, 1] + perm
    L2 = [0] * (n + 1); R2 = [0] * (n + 1)
    for v in range(1, n + 1):
        L2[perm[v]] = perm[Lc[v]] if Lc[v] else 0
        R2[perm[v]] = perm[Rc[v]] if Rc[v] else 0
    return L2, R2


def bin_text(n, L, R):
    return "\n".join("%d %d" % (L[i], R[i]) for i in range(1, n + 1))


def read_bin(it):
    n = int(next(it)); L = [0] * (n + 1); R = [0] * (n + 1)
    for i in range(1, n + 1):
        L[i] = int(next(it)); R[i] = int(next(it))
    return n, L, R


def pre_bin(L, R):
    out = []; st = [1]
    while st:
        v = st.pop(); out.append(v)
        if R[v]: st.append(R[v])
        if L[v]: st.append(L[v])
    return out


def in_bin(L, R):
    out = []; st = []; cur = 1
    while st or cur:
        while cur:
            st.append(cur); cur = L[cur]
        cur = st.pop(); out.append(cur); cur = R[cur]
    return out


def post_bin(L, R):
    out = []; st = [1]
    while st:
        v = st.pop(); out.append(v)
        if L[v]: st.append(L[v])
        if R[v]: st.append(R[v])
    return out[::-1]


def bst_shape(r, n):
    """binary tree shape + strictly increasing-by-inorder values; returns L,R,val"""
    L, R = rbin(r, n)
    io = in_bin(L, R)
    vs = sorted(r.sample(range(1, 10 * n + 10), n))
    val = [0] * (n + 1)
    for k, v in enumerate(io): val[v] = vs[k]
    return L, R, val


def J(a, sep=" "):
    return sep.join(map(str, a))


def rword(r, alpha, lo, hi):
    return "".join(r.choice(alpha) for _ in range(r.randint(lo, hi)))


class Fen:
    def __init__(s, n):
        s.n = n; s.t = [0] * (n + 1)

    def add(s, i, v):
        while i <= s.n:
            s.t[i] += v; i += i & -i

    def sum(s, i):
        x = 0
        while i > 0:
            x += s.t[i]; i -= i & -i
        return x

    def kth(s, k):
        """smallest i with prefix sum >= k (counts nonneg)"""
        pos = 0; step = 1
        while step * 2 <= s.n: step *= 2
        while step:
            if pos + step <= s.n and s.t[pos + step] < k:
                pos += step; k -= s.t[pos]
            step //= 2
        return pos + 1


def gt(r, lv, tiny=8, big=100000):
    n = sz(r, lv, tiny, big)
    return n, rtree(r, n)


def rd(inp):
    it = iter(inp.split()); n = int(next(it)); adj = read_edges(it, n)
    return n, adj



# ---- запросы: общие
def gq(r, lv, k, extra=None, qmax=100000):
    n, ed = gt(r, lv)
    q = sz(r, lv, 6, qmax)
    qs = []
    for _ in range(q):
        qs.append(tuple(r.randint(1, n) for _ in range(k)))
    return n, ed, q, qs
def rdq(inp, wts=False):
    it = iter(inp.split()); n = int(next(it)); q = int(next(it))
    w = None
    if wts: w = [0] + [int(next(it)) for _ in range(n)]
    adj = read_edges(it, n)
    return n, q, w, adj, it



def rdw(inp):
    it = iter(inp.split()); n = int(next(it)); w = [0] + [int(next(it)) for _ in range(n)]
    return n, w, read_edges(it, n)

def dia(n, adj):
    d = bfs_dist(n, adj, 1); a = d.index(max(d))
    d2 = bfs_dist(n, adj, a); bb = d2.index(max(d2))
    return a, bb, d2[bb]


def gb(r, lv, tiny=8, big=100000):
    n = sz(r, lv, tiny, big)
    L, R = rbin(r, n)
    return n, L, R


def rdb(inp):
    it = iter(inp.split())
    return read_bin(it)


def gbt(r, lv):
    n, L, R = gb(r, lv)
    return "%d\n%s\n" % (n, bin_text(n, L, R))


def levels_bin(L, R):
    res = []; cur = [1]
    while cur:
        res.append(cur); nxt = []
        for v in cur:
            if L[v]: nxt.append(L[v])
            if R[v]: nxt.append(R[v])
        cur = nxt
    return res


def bst_build(vals):
    """insert vals in order; nodes are 1..n by insertion index; returns L,R,depth(levels, root=1)"""
    n = len(vals)
    L = [0] * (n + 1); R = [0] * (n + 1); dep = [0] * (n + 1); dep[1] = 1
    for i in range(2, n + 1):
        v = 1; x = vals[i - 1]
        while True:
            if x < vals[v - 1]:
                if L[v]: v = L[v]
                else: L[v] = i; break
            else:
                if R[v]: v = R[v]
                else: R[v] = i; break
        dep[i] = dep[v] + 1
    return L, R, dep


def gvals(r, lv, tiny=8, big=2000):
    n = sz(r, lv, tiny, big)
    return n, r.sample(range(1, 4 * n + 6), n)


class DSU:
    def __init__(s, n):
        s.p = list(range(n + 1)); s.sz = [1] * (n + 1); s.c = n

    def find(s, x):
        r = x
        while s.p[r] != r: r = s.p[r]
        while s.p[x] != r: s.p[x], x = r, s.p[x]
        return r

    def union(s, a, b):
        a = s.find(a); b = s.find(b)
        if a == b: return False
        if s.sz[a] < s.sz[b]: a, b = b, a
        s.p[b] = a; s.sz[a] += s.sz[b]; s.c -= 1
        return True


def gedges(r, lv, tiny=8, big=100000, mfac=1.5):
    n = sz(r, lv, tiny, big); m = max(1, int(n * r.choice([0.3, 0.7, mfac])))
    if n == 1: m = 0
    es = []
    for _ in range(m):
        a = r.randint(1, n); b = r.randint(1, n)
        while b == a and n > 1: b = r.randint(1, n)
        es.append((a, b))
    return n, es


def rdg(inp, w=False):
    it = iter(inp.split()); n = int(next(it)); m = int(next(it)); es = []
    for _ in range(m):
        a = int(next(it)); b = int(next(it)); c = int(next(it)) if w else 0
        es.append((a, b, c))
    return n, m, es, it


def comps_bfs(n, es):
    adj = [[] for _ in range(n + 1)]
    for a, b, *_ in es: adj[a].append(b); adj[b].append(a)
    seen = [False] * (n + 1); c = 0
    for s0 in range(1, n + 1):
        if not seen[s0]:
            c += 1; seen[s0] = True; st = [s0]
            while st:
                v = st.pop()
                for u in adj[v]:
                    if not seen[u]: seen[u] = True; st.append(u)
    return c


def gops(r, lv, vmin, vmax, kinds, big=100000):
    n = sz(r, lv, 8, big); q = sz(r, lv, 8, big)
    a = [r.randint(vmin, vmax) for _ in range(n)]
    ops = []
    def mk(k):
        f = kinds[k]
        if f == 'P': s = "%d %d" % (r.randint(1, n), r.randint(vmin, vmax))
        elif f == 'R':
            l = r.randint(1, n); s = "%d %d" % (l, r.randint(l, n))
        elif f == 'RX':
            l = r.randint(1, n); s = "%d %d %d" % (l, r.randint(l, n), r.randint(vmin, vmax))
        elif f == 'I': s = "%d" % r.randint(1, n)
        else: s = "%d" % r.randint(1, n)
        return "%d %s" % (k + 1, s)
    for _ in range(q): ops.append(mk(r.randrange(len(kinds))))
    ops.append(mk(len(kinds) - 1))
    return "%d %d\n%s\n%s\n" % (n, len(ops), J(a), "\n".join(ops))


def rdo(inp):
    it = iter(inp.split()); n = int(next(it)); q = int(next(it))
    a = [int(next(it)) for _ in range(n)]
    ops = []
    for line in inp.split("\n")[2:]:
        if line.strip(): ops.append(list(map(int, line.split())))
    return n, q, a, ops


class SegT:
    def __init__(s, a, f, e):
        s.n = len(a); s.f = f; s.e = e; s.N = 1
        while s.N < s.n: s.N *= 2
        s.t = [e] * (2 * s.N)
        for i, x in enumerate(a): s.t[s.N + i] = x
        for i in range(s.N - 1, 0, -1): s.t[i] = f(s.t[2 * i], s.t[2 * i + 1])

    def set(s, i, x):
        i += s.N; s.t[i] = x; i >>= 1
        while i:
            s.t[i] = s.f(s.t[2 * i], s.t[2 * i + 1]); i >>= 1

    def query(s, l, r):
        l += s.N; r += s.N; a = s.e; b = s.e
        while l < r:
            if l & 1: a = s.f(a, s.t[l]); l += 1
            if r & 1: r -= 1; b = s.f(s.t[r], b)
            l >>= 1; r >>= 1
        return s.f(a, b)


class XT:
    def __init__(s, bits=30):
        s.b = bits; s.c0 = [-1]; s.c1 = [-1]

    def ins(s, x):
        v = 0
        for i in range(s.b - 1, -1, -1):
            c = s.c1 if x >> i & 1 else s.c0
            if c[v] < 0:
                c[v] = len(s.c0); s.c0.append(-1); s.c1.append(-1)
            v = c[v]

    def best(s, x):
        v = 0; r = 0
        for i in range(s.b - 1, -1, -1):
            bit = x >> i & 1
            want = s.c0 if bit else s.c1
            if want[v] >= 0:
                r |= 1 << i; v = want[v]
            else:
                v = (s.c1 if bit else s.c0)[v]
        return r


def gwords(r, lv, tiny=6, big=20000, lo=1, hi=10, distinct=False):
    n = sz(r, lv, tiny, big); al = r.choice(["ab", "abc", "abcdefgh"])
    ws = [rword(r, al, lo, hi) for _ in range(n)]
    if distinct:
        ws = list(dict.fromkeys(ws))
    return ws, al


def rdv(inp):
    it = iter(inp.split()); n = int(next(it)); S = int(next(it))
    w = [0] + [int(next(it)) for _ in range(n)]
    L = [0] * (n + 1); R = [0] * (n + 1)
    for i in range(1, n + 1): L[i] = int(next(it)); R[i] = int(next(it))
    return n, S, w, L, R

def rdi(inp):
    it = iter(inp.split()); n = int(next(it)); return n, [int(next(it)) for _ in range(n)]

def rdt(inp):
    it = iter(inp.split()); n = int(next(it)); w = [0] + [int(next(it)) for _ in range(n)]
    L = [0] * (n + 1); R = [0] * (n + 1)
    for i in range(1, n + 1): L[i] = int(next(it)); R[i] = int(next(it))
    return n, w, L, R

def rds(inp):
    ls = inp.split("\n"); n, q = map(int, ls[0].split()); st = ls[1].strip()
    return n, q, st, [tuple(map(int, x.split())) for x in ls[2:2 + q]]


def b(inp):
    it = iter(inp.split()); n = int(next(it)); K = int(next(it)); a = [int(next(it)) for _ in range(n)]
    return "YES" if any(a[i] + a[j] == K for i in range(n) for j in range(i + 1, n)) else "NO"


if __name__ == '__main__':
    print(b(sys.stdin.read()))
