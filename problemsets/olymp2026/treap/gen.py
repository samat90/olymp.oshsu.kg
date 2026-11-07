"""gen.py n q maxA seed (keeps the queue length known, never empty, at most 4e5)"""
import random
import sys

n, q, A, s = (int(x) for x in sys.argv[1:5])
random.seed(s * 1213 + n)
cur = n
lines = ['%d %d' % (n, q), ' '.join(str(random.randint(0, A)) for _ in range(n))]
for _ in range(q):
    t = random.choice([1, 1, 2, 3, 4, 5])
    if t == 3 and cur == 1:
        t = 2
    if t == 2 and cur >= 400000 - 1:
        t = 4
    if t in (1, 4, 5):
        l, r = sorted((random.randint(1, cur), random.randint(1, cur)))
        lines.append('%d %d %d' % (t, l, r))
    elif t == 2:
        lines.append('2 %d %d' % (random.randint(0, cur), random.randint(0, A)))
        cur += 1
    else:
        lines.append('3 %d' % random.randint(1, cur))
        cur -= 1
print('\n'.join(lines))
