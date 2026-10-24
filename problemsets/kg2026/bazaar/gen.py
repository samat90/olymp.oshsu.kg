"""gen.py n q shape(rand/short/long) assign(0/1) seed"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, write  # noqa: E402

n, q, shape, assign, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), sys.argv[5]
seed(s)
lines = ['%d %d' % (n, q), ' '.join(str(random.randint(0, 10 ** 9)) for _ in range(n))]
for _ in range(q):
    if shape == 'long':
        l = random.randint(1, max(1, n // 10)); r = random.randint(n - n // 10, n)
    elif shape == 'short':
        l = random.randint(1, n); r = min(n, l + random.randint(0, 5))
    else:
        l, r = sorted((random.randint(1, n), random.randint(1, n)))
    c = random.random()
    t = 3 if c < 0.35 else (1 if not assign or c < 0.75 else 2)
    if t == 3:
        lines.append('3 %d %d' % (l, r))
    elif t == 1:
        lines.append('1 %d %d %d' % (l, r, random.randint(-10 ** 4, 10 ** 4)))
    else:
        lines.append('2 %d %d %d' % (l, r, random.choice([0, 10 ** 9, random.randint(0, 10 ** 9)])))
write(lines)
