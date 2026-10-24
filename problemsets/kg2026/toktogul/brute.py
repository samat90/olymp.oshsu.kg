# Enumerates every integer flow on every canal (tiny tests only).
import itertools
import sys

d = sys.stdin.read().split()
n, m, F = int(d[0]), int(d[1]), int(d[2])
edges = [tuple(int(x) for x in d[3 + 5 * i:8 + 5 * i]) for i in range(m)]
best = None
for flows in itertools.product(*[range(l, c + 1) for (_, _, l, c, _) in edges]):
    bal = [0] * (n + 1)
    for (u, v, _, _, _), f in zip(edges, flows):
        bal[u] -= f
        bal[v] += f
    bal[1] += F
    bal[n] -= F
    if any(bal[1:]):
        continue
    cost = sum(f * e[4] for f, e in zip(flows, edges))
    if best is None or cost < best:
        best = cost
print(best if best is not None else -1)
