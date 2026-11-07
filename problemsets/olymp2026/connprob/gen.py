"""gen.py n m mode(rand/edge/cycle/half) seed; edge: many roads with p = 0 or 100"""
import random
import sys

n, m, mode, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
random.seed(s * 19 + n * 7 + m)
E = []
if n == 1:
    m = 0
if mode == 'cycle':
    for i in range(n):
        if len(E) < m:
            E.append((i, (i + 1) % n))
while len(E) < m:
    u, v = random.sample(range(n), 2)
    E.append((u, v))
out = []
for u, v in E:
    if mode == 'edge':
        p = random.choice([0, 100, 100, random.randint(0, 100)])
    elif mode == 'half':
        p = 50
    else:
        p = random.randint(0, 100)
    out.append('%d %d %d' % (u + 1, v + 1, p))
print(n, m)
print('\n'.join(out))
