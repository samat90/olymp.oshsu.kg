"""gen.py n q removals(0/1) mode(rand/local/flood/path) seed

flood: the river rises and falls: long waves of building, then of washing bridges away.
local: bridges mostly between neighbouring villages along the river.
path:  bridges i - i+1 only, removed and rebuilt.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, write  # noqa: E402

n, q, removals, mode, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
seed(s)
alive = []
lines = ['%d %d' % (n, q)]


def pair():
    if mode in ('local', 'flood'):
        a = random.randint(1, n)
        b = min(n, max(1, a + random.choice([-2, -1, 1, 2, random.randint(-50, 50)])))
        if a == b:
            b = a % n + 1
        return a, b
    if mode == 'path':
        a = random.randint(1, max(1, n - 1))
        return a, a + 1
    a = random.randint(1, n)
    b = random.randint(1, n)
    while b == a and n > 1:
        b = random.randint(1, n)
    return a, b


phase_len = max(1, q // 10)
for i in range(q):
    building = (i // phase_len) % 2 == 0 if mode == 'flood' else random.random() < 0.6
    c = random.random()
    if n == 1:
        lines.append('C' if c < 0.5 else '? 1 1')
        continue
    if c < 0.45:
        if removals and alive and not building:
            j = random.randrange(len(alive))
            alive[j], alive[-1] = alive[-1], alive[j]
            a, b = alive.pop()
            lines.append('- %d %d' % ((a, b) if random.random() < 0.5 else (b, a)))
        else:
            e = pair()
            if alive and random.random() < 0.05:
                e = random.choice(alive)  # a second bridge between the same villages
            alive.append(e)
            lines.append('+ %d %d' % e)
    elif c < 0.85:
        a = random.randint(1, n)
        b = random.randint(1, n) if random.random() < 0.4 else min(n, max(1, a + random.randint(-30, 30)))
        lines.append('? %d %d' % (a, b))
    else:
        lines.append('C')
write(lines)
