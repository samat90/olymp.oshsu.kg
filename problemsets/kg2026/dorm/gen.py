"""gen.py n cmax forbid(0..1 fraction) mode(rand/structured/impossible/trap) seed"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, write  # noqa: E402

n, cmax, forbid, mode, s = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
seed(s)
rows = []
perm = random.sample(range(n), n)
for i in range(n):
    row = []
    for j in range(n):
        if mode == 'structured':
            x = abs(i - j) * random.randint(1, 3) + random.randint(0, cmax // 100)
        elif mode == 'trap':
            # the obvious cheap cells form a trap for greedy choices
            x = random.randint(cmax // 2, cmax) if j != perm[i] else random.randint(0, cmax // 3)
            if j == (perm[i] + 1) % n:
                x = random.randint(0, cmax // 4)
        else:
            x = random.randint(0, cmax)
        if random.random() < forbid and not (mode != 'impossible' and j == perm[i]):
            x = -1
        row.append(min(x, cmax))
    rows.append(row)
if mode == 'impossible' and n >= 2:
    # two students can only go to the same single room
    for j in range(n):
        rows[0][j] = rows[1][j] = -1
    rows[0][0] = rows[1][0] = random.randint(0, cmax)
write([str(n)] + [' '.join(map(str, r)) for r in rows])
