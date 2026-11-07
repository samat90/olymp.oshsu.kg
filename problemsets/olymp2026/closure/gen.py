"""gen.py n m pmax mode(rand/layers/chain/bip) seed"""
import random
import sys

n, m, P, mode, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
random.seed(s * 577 + n)
p = [random.randint(-P, P) for _ in range(n)]
E = set()
m = min(m, n * (n - 1))
if mode == 'bip':  # profitable projects depend on expensive infrastructure
    k = max(1, n // 3)
    infra = list(range(k))
    for i in infra:
        p[i] = -random.randint(1, P)
    for i in range(k, n):
        p[i] = random.randint(0, P)
    while len(E) < m:
        a, b = random.randrange(k, n) if n > k else 0, random.choice(infra)
        if a != b:
            E.add((a, b))
elif mode == 'layers':
    L = random.randint(2, 8)
    while len(E) < m:
        a, b = random.sample(range(n), 2)
        if a % L != b % L:
            E.add((a, b))
elif mode == 'chain':
    for i in range(n - 1):
        if len(E) < m:
            E.add((i, i + 1))
    while len(E) < m:
        a, b = random.sample(range(n), 2)
        E.add((a, b))
else:
    while len(E) < m:
        a, b = random.sample(range(n), 2)
        E.add((a, b))
perm = list(range(1, n + 1))
random.shuffle(perm)
E = list(E)
random.shuffle(E)
q = [0] * n
for i in range(n):
    q[perm[i] - 1] = p[i]
print(n, len(E))
print(' '.join(map(str, q)))
print('\n'.join('%d %d' % (perm[a], perm[b]) for a, b in E))
