"""gen.py n q kmax free(0/1) mode(rand/big/tiny/wrap) seed"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, write  # noqa: E402

n, q, kmax, allow_free = [int(x) for x in sys.argv[1:5]]
mode, s = sys.argv[5], sys.argv[6]
seed(s)
lines = ['%d %d' % (n, q)]
for i in range(q):
    c = random.random()
    if c < 0.5 or (not allow_free and c < 0.8):
        if mode == 'tiny':
            k = random.randint(1, min(kmax, 4))
        elif mode == 'big':
            k = random.choice([random.randint(1, kmax), random.randint(kmax // 2 + 1, kmax), n, n + 1])
        else:
            k = random.randint(1, kmax)
        lines.append('+ %d' % max(1, k))
    elif c < 0.8:
        l = random.randint(1, n)
        if mode == 'wrap':
            l = random.randint(max(1, n - kmax), n)
        length = random.randint(1, min(n, 2 * kmax))
        lines.append('- %d %d' % (l, (l + length - 2) % n + 1))
    else:
        l = random.randint(1, n)
        length = random.randint(1, n)
        lines.append('? %d %d' % (l, (l + length - 2) % n + 1))
write(lines)
