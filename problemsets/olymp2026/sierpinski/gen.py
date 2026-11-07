"""gen.py k q mode(rand/aligned/big/line/point) seed"""
import random
import sys

k, q, mode, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
random.seed(s * 7919 + k)
n = 3 ** k


def pick():
    if mode in ('aligned', 'line', 'point') and random.random() < 0.7:  # near block borders
        j = random.randint(0, k)
        v = random.randrange(0, 3 ** (k - j) + 1) * 3 ** j + random.choice([-1, 0, 0, 1])
        return min(n - 1, max(0, v))
    return random.randrange(n)


lines = ['%d %d' % (k, q)]
for _ in range(q):
    if mode == 'big':
        m = max(1, n // 10)
        x1, y1 = random.randrange(m), random.randrange(m)
        x2, y2 = n - 1 - random.randrange(m), n - 1 - random.randrange(m)
    elif mode == 'point':
        x1 = x2 = pick()
        y1 = y2 = pick()
    elif mode == 'line':
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
    lines.append('%d %d %d %d' % (x1, y1, x2, y2))
print('\n'.join(lines))
