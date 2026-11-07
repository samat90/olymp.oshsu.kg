"""gen.py n q maxColour updateShare seed"""
import random
import sys

n, q, C, share, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
random.seed(s * 677 + n)
pal = [random.randint(1, C) for _ in range(min(C, 1000))] if C > 1000 else list(range(1, C + 1))
col = lambda: random.choice(pal) if random.random() < 0.7 else random.randint(1, C)  # noqa: E731
lines = ['%d %d' % (n, q), ' '.join(str(col()) for _ in range(n))]
for _ in range(q):
    if random.random() < share:
        lines.append('1 %d %d' % (random.randint(1, n), col()))
    else:
        l, r = sorted((random.randint(1, n), random.randint(1, n)))
        if random.random() < 0.2:
            l, r = random.randint(1, max(1, n // 10)), random.randint(n - n // 10, n)
            l, r = min(l, r), max(l, r)
        lines.append('2 %d %d' % (l, r))
print('\n'.join(lines))
