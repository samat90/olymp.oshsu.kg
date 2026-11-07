import sys
from itertools import combinations

d = sys.stdin.read().split()
T = int(d[0])
pos = 1
cache = {}


def table(n):
    if n in cache:
        return cache[n]
    pairs = list(combinations(range(n), 2))
    res = {}
    for mask in range(1 << len(pairs)):
        deg = [0] * n
        par = list(range(n))

        def f(x):
            while par[x] != x:
                x = par[x]
            return x
        comps = n
        for i, (a, b) in enumerate(pairs):
            if mask >> i & 1:
                deg[a] += 1
                deg[b] += 1
                ra, rb = f(a), f(b)
                if ra != rb:
                    par[ra] = rb
                    comps -= 1
        key = tuple(sorted(deg))
        res[key] = res.get(key, False) or comps == 1
    cache[n] = res
    return res


out = []
for _ in range(T):
    n = int(d[pos])
    seq = tuple(sorted(int(x) for x in d[pos + 1:pos + 1 + n]))
    pos += 1 + n
    t = table(n)
    if seq in t:
        out.append('YES ' + ('YES' if t[seq] else 'NO'))
    else:
        out.append('NO NO')
print('\n'.join(out))
