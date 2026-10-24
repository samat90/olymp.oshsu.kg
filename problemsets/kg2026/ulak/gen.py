"""gen.py n m q totalk maxk shape(random/layers/complete/chain) seed"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, write  # noqa: E402

n, m, q, total, maxk = [int(x) for x in sys.argv[1:6]]
shape, s = sys.argv[6], sys.argv[7]
seed(s)
edges = set()
if shape == 'complete':
    t = 1
    while (t + 1) * t // 2 <= m and t < n:
        t += 1
    for i in range(t):
        for j in range(i + 1, t):
            if len(edges) < m:
                edges.add((i, j))
if shape == 'chain':
    for i in range(n - 1):
        edges.add((i, i + 1))
        if i + 2 < n and random.random() < 0.5:
            edges.add((i, i + 2))
tries = 0
while len(edges) < m and tries < 20 * m:
    tries += 1
    if shape == 'layers':
        a = random.randrange(n - 1)
        b = min(n - 1, a + random.randint(1, 3))
    else:
        a, b = sorted(random.sample(range(n), 2))
    edges.add((a, b))
edges = list(edges)[:m]
perm = list(range(1, n + 1))
random.shuffle(perm)
random.shuffle(edges)
lines = ['%d %d' % (n, len(edges))] + ['%d %d' % (perm[a], perm[b]) for a, b in edges]
lines.append(str(q))
left = total
for i in range(q):
    k = max(1, min(maxk, left - (q - i - 1))) if i == q - 1 else random.randint(1, max(1, min(maxk, left - (q - i - 1))))
    left -= k
    if shape == 'complete' and random.random() < 0.7:
        pos = [perm[random.randrange(min(n, 800))] for _ in range(k)]
    else:
        pos = [random.randint(1, n) for _ in range(k)]
    lines.append('%d %s' % (k, ' '.join(map(str, pos))))
write(lines)
