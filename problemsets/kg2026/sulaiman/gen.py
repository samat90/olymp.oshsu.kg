"""gen.py n q shape updates(0/1) maxh seed"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, tree, write  # noqa: E402

n, q, shape, updates, maxh, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), \
    int(sys.argv[5]), sys.argv[6]
seed(s)
edges = tree(n, shape, shuffle=(shape != 'pathfixed'))
if shape == 'pathfixed':
    edges = [(i, i + 1) for i in range(1, n)]
lines = [str(n), ' '.join(str(random.randint(1, maxh)) for _ in range(n))]
lines += ['%d %d' % e for e in edges]
lines.append(str(q))
for _ in range(q):
    if updates and random.random() < 0.4:
        lines.append('1 %d %d' % (random.randint(1, n), random.randint(1, maxh)))
    else:
        lines.append('2 %d %d' % (random.randint(1, n), random.randint(1, n)))
write(lines)
