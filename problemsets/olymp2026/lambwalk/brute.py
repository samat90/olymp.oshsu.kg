# Solve the linear system for the hitting times with exact fractions.
import sys
from fractions import Fraction

d = sys.stdin.read().split()
n, q = int(d[0]), int(d[1])
adj = [[] for _ in range(n + 1)]
pos = 2
for _ in range(n - 1):
    u, v, w = int(d[pos]), int(d[pos + 1]), int(d[pos + 2])
    pos += 3
    adj[u].append((v, w))
    adj[v].append((u, w))
P = 998244353
cache = {}


def hitting(t):
    # unknowns E[v] for v != t: E[v] = 1 + sum p(v,u) E[u]
    vs = [v for v in range(1, n + 1) if v != t]
    idx = {v: i for i, v in enumerate(vs)}
    m = len(vs)
    A = [[Fraction(0)] * (m + 1) for _ in range(m)]
    for v in vs:
        i = idx[v]
        A[i][i] += 1
        tot = sum(w for _, w in adj[v])
        for u, w in adj[v]:
            if u != t:
                A[i][idx[u]] -= Fraction(w, tot)
        A[i][m] = Fraction(1)
    for c in range(m):
        p = next(r for r in range(c, m) if A[r][c] != 0)
        A[c], A[p] = A[p], A[c]
        for r in range(m):
            if r != c and A[r][c] != 0:
                f = A[r][c] / A[c][c]
                A[r] = [a - f * b for a, b in zip(A[r], A[c])]
    res = {t: Fraction(0)}
    for v in vs:
        i = idx[v]
        res[v] = A[i][m] / A[i][i]
    return res


out = []
for _ in range(q):
    s, t = int(d[pos]), int(d[pos + 1])
    pos += 2
    if t not in cache:
        cache[t] = hitting(t)
    e = cache[t][s]
    out.append(e.numerator % P * pow(e.denominator % P, P - 2, P) % P)
print('\n'.join(map(str, out)))
