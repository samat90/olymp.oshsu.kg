"""gen.py n sigma mode(rand/periodic/fib/runs/blocks) seed"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, write  # noqa: E402

n, sigma, mode, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]
seed(s)
notes = list(range(1, sigma + 1)) if sigma <= 26 else random.sample(range(1, 10 ** 9 + 1), sigma)
pick = lambda: random.choice(notes)
if mode == 'periodic':
    base = [pick() for _ in range(random.randint(1, 50))]
    a = [base[i % len(base)] for i in range(n)]
    for _ in range(random.randint(0, 5)):
        a[random.randrange(n)] = pick()
elif mode == 'fib':
    x, y = [notes[0]], [notes[1 % sigma]]
    while len(y) < n:
        x, y = y, y + x
    a = y[:n]
elif mode == 'runs':
    a = []
    while len(a) < n:
        a += [pick()] * random.randint(1, 1000)
    a = a[:n]
elif mode == 'blocks':
    blocks = [[pick() for _ in range(random.randint(1, 20))] for _ in range(5)]
    a = []
    while len(a) < n:
        a += random.choice(blocks)
    a = a[:n]
else:
    a = [pick() for _ in range(n)]
write([str(n), ' '.join(map(str, a))])
