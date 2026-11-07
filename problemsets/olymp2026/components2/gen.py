"""gen.py n shape seed"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, tree  # noqa: E402

n, shape, s = int(sys.argv[1]), sys.argv[2], sys.argv[3]
seed(s)
mode = random.random()
ps = []
for _ in range(n):
    if mode < 0.3:
        ps.append(random.randint(0, 100))
    elif mode < 0.6:
        ps.append(random.choice([0, 100, 50, 1, 99, random.randint(0, 100)]))
    else:
        ps.append(random.randint(30, 70))
print(n)
print(' '.join(map(str, ps)))
print('\n'.join('%d %d' % e for e in tree(n, shape)))
