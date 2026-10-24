import sys
from collections import Counter

d = sys.stdin.read().split()
n, q = int(d[0]), int(d[1])
p = 2
edges = Counter()
out = []


def components():
    par = list(range(n + 1))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for (a, b) in edges:
        par[f(a)] = f(b)
    return par, f


for _ in range(q):
    c = d[p]
    p += 1
    if c == 'C':
        par, f = components()
        out.append(str(sum(1 for v in range(1, n + 1) if f(v) == v)))
        continue
    a, b = sorted((int(d[p]), int(d[p + 1])))
    p += 2
    if c == '+':
        edges[(a, b)] += 1
    elif c == '-':
        edges[(a, b)] -= 1
        if not edges[(a, b)]:
            del edges[(a, b)]
    else:
        par, f = components()
        out.append('YES' if f(a) == f(b) else 'NO')
print('\n'.join(out))
