import sys
from itertools import combinations

d = sys.stdin.read().split()
n, m = int(d[0]), int(d[1])
E = [(int(d[2 + 3 * i]), int(d[3 + 3 * i]), int(d[4 + 3 * i])) for i in range(m)]
best, cnt = None, 0
for sub in combinations(range(m), n - 1):
    par = list(range(n + 1))

    def f(x):
        while par[x] != x:
            x = par[x]
        return x
    ok = True
    for i in sub:
        a, b = f(E[i][0]), f(E[i][1])
        if a == b:
            ok = False
            break
        par[a] = b
    if not ok:
        continue
    w = sum(E[i][2] for i in sub)
    if best is None or w < best:
        best, cnt = w, 1
    elif w == best:
        cnt += 1
print(-1 if best is None else '%d %d' % (best, cnt % 1000000007))
