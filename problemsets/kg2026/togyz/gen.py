"""gen.py n m amax mode(classic/rand/huge/few) seed

classic: n = 9, nine stones in every hole, like the real game.
huge:    counts up to amax (10^9), many full rounds per move.
few:     mostly empty holes, so skipped moves and single-stone moves are common.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, write  # noqa: E402

n, m, amax, mode, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
seed(s)
if mode == 'classic':
    a = [9] * (2 * n)
elif mode == 'few':
    a = [random.choice([0, 0, 0, 1, 1, 2, 3, random.randint(0, amax)]) for _ in range(2 * n)]
elif mode == 'huge':
    a = [random.randint(amax // 2, amax) for _ in range(2 * n)]
else:
    a = [random.randint(0, amax) for _ in range(2 * n)]
moves = [random.randint(1, n) if random.random() < 0.8 else random.choice([1, n, max(1, n - 1)]) for _ in range(m)]
write([str(n), ' '.join(map(str, a)), str(m), ' '.join(map(str, moves))])
