"""gen.py n wmax vmax mode(rand/novalue/correlated/equal/tight) seed

W and V are chosen near the medians of the totals, so that the answer is neither 0 nor 2^n.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, write  # noqa: E402

n, wmax, vmax, mode, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
seed(s)
items = []
for _ in range(n):
    w = random.randint(1, wmax)
    if mode == 'novalue':
        v = 0
    elif mode == 'correlated':  # heavy things are useful: the hard case for pruning
        v = max(0, min(vmax, w * vmax // wmax + random.randint(-vmax // 100, vmax // 100)))
    elif mode == 'equal':
        w, v = wmax, vmax
    else:
        v = random.randint(0, vmax)
    items.append((w, v))
tw = sum(w for w, _ in items)
tv = sum(v for _, v in items)
if mode == 'novalue':
    V = 0
else:
    V = random.randint(tv // 3, max(tv // 3, tv * 2 // 3)) if random.random() < 0.9 else random.choice([0, tv, tv + 1])
W = random.randint(tw // 3, max(tw // 3, tw * 2 // 3))
if mode == 'tight':
    W, V = tw // 2, tv // 2
write(['%d %d %d' % (n, W, V)] + ['%d %d' % x for x in items])
