import sys
from itertools import product

d = sys.stdin.read().split()
T = int(d[0])
out = []
for t in range(T):
    n, k = int(d[1 + 2 * t]), int(d[2 + 2 * t])
    neck, brace = set(), set()
    for c in product(range(k), repeat=n):
        if any(c[i] == c[(i + 1) % n] for i in range(n)):
            continue
        rots = [c[i:] + c[:i] for i in range(n)]
        neck.add(min(rots))
        r = c[::-1]
        brace.add(min(rots + [r[i:] + r[:i] for i in range(n)]))
    out.append('%d %d' % (len(neck) % 1000000007, len(brace) % 1000000007))
print('\n'.join(out))
