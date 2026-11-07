"""gen.py n m mode(rand/hard/chain/unsat) seed
hard: clauses satisfied by a hidden random assignment, so the answer usually exists and is non-trivial."""
import random
import sys

n, m, mode, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
random.seed(s * 811 + n)
hid = [random.randint(0, 1) for _ in range(n)]
C = []
if mode == 'chain':  # long implication chains x1 -> x2 -> ... force propagation far away
    perm = list(range(n))
    random.shuffle(perm)
    for k in range(min(m, n - 1)):
        a, b = perm[k], perm[k + 1]
        # clause (a = 1 - hid[a]... ) keep it satisfied by hid
        C.append((a, 1 - hid[a], b, hid[b]))
while len(C) < m:
    i, j = random.randrange(n), random.randrange(n)
    if random.random() < 0.3 and n > 50:
        j = (i + random.randint(1, 20)) % n
    x, y = random.randint(0, 1), random.randint(0, 1)
    if mode in ('hard', 'chain') and not (hid[i] == x or hid[j] == y):
        if random.random() < 0.5:
            x = hid[i]
        else:
            y = hid[j]
    C.append((i, x, j, y))
if mode == 'unsat':  # a contradiction hidden in a cycle: v -> ... -> not v -> ... -> v
    v = random.randrange(n)
    others = [u for u in range(n) if u != v]
    extra = []
    for start, end in ((1, 0), (0, 1)):  # v=1 implies ... implies v=0, and v=0 implies ... implies v=1
        mid = [(u, random.randint(0, 1)) for u in random.sample(others, min(len(others), random.randint(2, 15)))]
        chain = [(v, start)] + mid + [(v, end)]
        for t in range(len(chain) - 1):
            (a, va), (b, vb) = chain[t], chain[t + 1]
            extra.append((a, 1 - va, b, vb))  # a=va implies b=vb
    C = C[:max(0, m - len(extra))] + extra
random.shuffle(C)
print(n, len(C))
print('\n'.join('%d %d %d %d' % (i + 1, x, j + 1, y) for i, x, j, y in C))
