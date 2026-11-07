"""gen.py T maxN maxH seed (the sum of N is kept within 1e7)"""
import random
import sys

T, N, H, s = (int(x) for x in sys.argv[1:5])
random.seed(s * 277 + T)
out = []
budget = 10 ** 7
for _ in range(T):
    n = random.randint(max(1, N // 2), N) if random.random() < 0.7 else random.randint(1, N)
    n = max(1, min(n, budget - (T - len(out) - 1)))
    budget -= n
    h = random.randint(1, H) if random.random() < 0.6 else H
    a = random.randint(0, h)
    if random.random() < 0.5:  # reachable parity, close to a
        b = a + random.randint(-min(n, h), min(n, h))
        b = min(h, max(0, b))
        if (a + b + n) % 2:
            b = b + 1 if b < h else b - 1
    else:
        b = random.randint(0, h)
    if random.random() < 0.15:
        a, b = random.choice([(0, 0), (h, h), (0, h), (h, 0)])
    out.append('%d %d %d %d' % (n, h, a, b))
print(T)
print('\n'.join(out))
