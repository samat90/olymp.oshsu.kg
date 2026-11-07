"""gen.py n m mode(rand/layers/chains/grid/wide) seed: a random DAG with hidden vertex order"""
import random
import sys

n, m, mode, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
random.seed(s * 997 + n)
perm = list(range(1, n + 1))
random.shuffle(perm)
E = set()
limit = n * (n - 1) // 2
m = min(m, limit)
if mode == 'chains':  # several long chains with a few links between them
    k = random.randint(2, max(2, n // 50))
    ch = [list(range(i, n, k)) for i in range(k)]
    for c in ch:
        for i in range(len(c) - 1):
            if len(E) < m:
                E.add((c[i], c[i + 1]))
    while len(E) < m:
        a, b = sorted(random.sample(range(n), 2))
        E.add((a, b))
elif mode in ('layers', 'wide'):
    L = random.randint(3, 12) if mode == 'layers' else 2
    lay = sorted(range(n), key=lambda x: x % L)
    layer = {v: v % L for v in range(n)}
    tries = 0
    while len(E) < m and tries < 50 * m:
        tries += 1
        a, b = random.sample(range(n), 2)
        if layer[a] > layer[b]:
            a, b = b, a
        if layer[a] == layer[b]:
            continue
        E.add((a, b))
    lay = None
    order = sorted(range(n), key=lambda v: (layer[v], v))
    pos = {v: i for i, v in enumerate(order)}
    E = {(a, b) if pos[a] < pos[b] else (b, a) for a, b in E}
elif mode == 'grid':  # points of a grid, edges between close dominating pairs
    w = int(n ** 0.5) + 1
    pts = [(random.randrange(10 * w), random.randrange(10 * w)) for _ in range(n)]
    idx = sorted(range(n), key=lambda i: pts[i])
    rank = {v: i for i, v in enumerate(idx)}
    tries = 0
    while len(E) < m and tries < 30 * m:
        tries += 1
        a, b = random.sample(range(n), 2)
        if pts[a][0] <= pts[b][0] and pts[a][1] <= pts[b][1] and rank[a] < rank[b]:
            E.add((rank[a], rank[b]))
        elif pts[b][0] <= pts[a][0] and pts[b][1] <= pts[a][1] and rank[b] < rank[a]:
            E.add((rank[b], rank[a]))
else:
    while len(E) < m:
        a, b = sorted(random.sample(range(n), 2))
        if random.random() < 0.7 and b - a > 60:
            b = a + random.randint(1, 60)
        E.add((a, b))
E = list(E)
random.shuffle(E)
print(n, len(E))
print('\n'.join('%d %d' % (perm[a], perm[b]) for a, b in E))
