"""gen.py n q wmax shape seed"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, tree  # noqa: E402

n, q, W, shape, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
seed(s)
edges = tree(n, shape)
lines = ['%d %d' % (n, q)] + ['%d %d %d' % (a, b, random.randint(1, W)) for a, b in edges]
for _ in range(q):
    a, b = random.randint(1, n), random.randint(1, n)
    if random.random() < 0.05:
        b = a
    lines.append('%d %d' % (a, b))
print('\n'.join(lines))
