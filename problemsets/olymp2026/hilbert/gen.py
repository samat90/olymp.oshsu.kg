"""gen.py k q mode(rand/thin/point/small/aligned) seed"""
import random
import sys

k, q, mode, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
random.seed(s * 2027 + k)
n = 1 << k


def pick():
    if mode == 'aligned' and k:
        j = random.randint(0, k)
        v = random.randrange(0, (n >> j) + 1) * (1 << j) + random.choice([-1, 0, 1])
        return min(n - 1, max(0, v))
    return random.randrange(n)


out = ['%d %d' % (k, q)]
for _ in range(q):
    if mode == 'point':
        x1 = x2 = pick()
        y1 = y2 = pick()
    elif mode == 'small':
        x1, y1 = pick(), pick()
        x2, y2 = min(n - 1, x1 + random.randint(0, 5)), min(n - 1, y1 + random.randint(0, 5))
    elif mode == 'thin':
        x1 = x2 = pick()
        a, b = pick(), pick()
        y1, y2 = min(a, b), max(a, b)
        if random.random() < 0.5:
            x1, x2, y1, y2 = y1, y2, x1, x2
    else:
        a, b = pick(), pick()
        x1, x2 = min(a, b), max(a, b)
        a, b = pick(), pick()
        y1, y2 = min(a, b), max(a, b)
    out.append('%d %d %d %d' % (x1, y1, x2, y2))
print('\n'.join(out))
