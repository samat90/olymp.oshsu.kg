# Enumerate all Pruefer codes.
import sys
from itertools import product

d = sys.stdin.read().split()
T = int(d[0])
out = []
for t in range(T):
    n, c, dd = int(d[1 + 3 * t]), int(d[2 + 3 * t]), int(d[3 + 3 * t])
    cnt = 0
    for code in product(range(1, n + 1), repeat=n - 2):
        deg = [1] * (n + 1)
        for v in code:
            deg[v] += 1
        if deg[1] == dd and sum(1 for v in range(1, n + 1) if deg[v] == 1) == c:
            cnt += 1
    out.append(cnt % 1000000007)
print('\n'.join(map(str, out)))
