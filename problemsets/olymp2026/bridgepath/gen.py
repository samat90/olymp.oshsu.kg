"""gen.py n m q mode(rand/tree/cactus/chain) seed: a connected multigraph"""
import random
import sys

n, m, q, mode, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
random.seed(s * 2459 + n)
perm = list(range(1, n + 1))
random.shuffle(perm)
E = []
if mode == 'chain':  # a path of blobs: many bridges on long paths
    for i in range(1, n):
        E.append((perm[i - 1], perm[i]))
else:
    for i in range(1, n):
        p = random.randrange(i) if mode != 'cactus' else max(0, i - random.randint(1, 3))
        E.append((perm[p], perm[i]))
while len(E) < m:
    if mode == 'cactus' or mode == 'chain':
        i = random.randrange(n)
        j = min(n - 1, i + random.randint(1, 4))
        if i == j:
            continue
        E.append((perm[i], perm[j]))
    elif mode == 'tree':
        a = random.randrange(1, n) if n > 1 else 0
        E.append(E[random.randrange(len(E))])  # a parallel edge
    else:
        a, b = random.sample(range(n), 2) if n > 1 else (0, 0)
        E.append((perm[a], perm[b]))
E = E[:m] if m >= n - 1 else E
random.shuffle(E)
lines = ['%d %d %d' % (n, len(E), q)] + ['%d %d' % e for e in E]
for _ in range(q):
    lines.append('%d %d' % (random.randint(1, n), random.randint(1, n)))
print('\n'.join(lines))
