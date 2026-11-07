"""gen.py n m mode(euler/rand/dense/loops/twocomp/ring/isolated) seed
Balanced graphs are built from random closed walks, so most tests have many routes."""
import random
import sys

n, m, mode, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
random.seed(s * 7 + n * 13 + m)


def cycles(vs, total, loops=0.0):
    """Union of random closed walks (a loop is a closed walk of length 1): always balanced."""
    arcs = []
    while len(arcs) < total:
        left = total - len(arcs)
        if random.random() < loops or len(vs) == 1:
            u = random.choice(vs)
            arcs.append((u, u))
            continue
        L = min(left, random.randint(2, max(2, min(len(vs) * 2, 40))))
        if L == 1:
            u = random.choice(vs)
            arcs.append((u, u))
            continue
        walk = [random.choice(vs) for _ in range(L)]
        for i in range(L):
            arcs.append((walk[i], walk[(i + 1) % L]))
    return arcs


vs = list(range(1, n + 1))
if mode == 'rand':
    arcs = [(random.randint(1, n), random.randint(1, n)) for _ in range(m)]
elif mode == 'dense':
    arcs = cycles(vs, m, 0.0)
elif mode == 'loops':
    arcs = cycles(vs, m, 0.3)
elif mode == 'twocomp':
    h = max(1, n // 2)
    arcs = cycles(vs[:h], m // 2) + cycles(vs[h:] or vs[:1], m - m // 2)
elif mode == 'ring':  # one big cycle plus chords made of short cycles
    arcs = [(i, i % n + 1) for i in range(1, n + 1)]
    arcs = arcs[:m] if m >= n else arcs
    arcs += cycles(vs, max(0, m - len(arcs)))
elif mode == 'isolated':
    used = random.sample(vs, max(2, n // 3))
    arcs = cycles(used, m)
else:
    arcs = cycles(vs, m)
first = arcs[:]
random.shuffle(first)
arcs = first[:m]
print(n, len(arcs))
print('\n'.join('%d %d' % x for x in arcs))
