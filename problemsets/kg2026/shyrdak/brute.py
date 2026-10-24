import itertools
import sys

d = sys.stdin.read().split()
t = int(d[0])
out = []
for i in range(t):
    n, k = int(d[1 + 2 * i]), int(d[2 + 2 * i])
    seen = set()
    for col in itertools.product(range(k), repeat=n):
        if any(col[j] == col[(j + 1) % n] for j in range(n)):
            continue
        seen.add(min(col[j:] + col[:j] for j in range(n)))
    out.append(str(len(seen) % (10 ** 9 + 7)))
print('\n'.join(out))
