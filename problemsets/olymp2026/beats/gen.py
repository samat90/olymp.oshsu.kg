"""gen.py n q maxA mode(rand/chmin/wave) seed"""
import random
import sys

n, q, A, mode, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
random.seed(s * 433 + n)
a = [random.randint(-A, A) for _ in range(n)]
lines = ['%d %d' % (n, q), ' '.join(map(str, a))]
level = A
for i in range(q):
    l, r = sorted((random.randint(1, n), random.randint(1, n)))
    if random.random() < 0.3:
        l, r = 1, n
    if mode == 'chmin':
        t = random.choice([1, 1, 3, 4])
    elif mode == 'wave':  # decreasing chmin levels with adds in between: hard for the amortisation
        t = random.choice([1, 2, 2, 3, 4])
    else:
        t = random.randint(1, 4)
    if t == 1:
        if mode == 'wave':
            level -= random.randint(0, max(1, 2 * A // q))
            x = level
        else:
            x = random.randint(-A, A)
        lines.append('1 %d %d %d' % (l, r, x))
    elif t == 2:
        lines.append('2 %d %d %d' % (l, r, random.randint(-10 ** 4, 10 ** 4)))
    else:
        lines.append('%d %d %d' % (t, l, r))
print('\n'.join(lines))
