"""gen.py n q maxA seed: x, y, z are random; after decoding with the previous answer they give random l, r, k"""
import random
import sys

n, q, A, s = (int(x) for x in sys.argv[1:5])
random.seed(s * 5281 + n)
mode = random.random()
if mode < 0.3:
    a = [random.randint(0, A) for _ in range(n)]
elif mode < 0.6:
    a = sorted(random.randint(0, A) for _ in range(n))
    if random.random() < 0.5:
        a.reverse()
else:
    pal = [random.randint(0, A) for _ in range(random.randint(1, 50))]
    a = [random.choice(pal) for _ in range(n)]
lines = ['%d %d' % (n, q), ' '.join(map(str, a))]
for _ in range(q):
    lines.append('%d %d %d' % (random.randint(0, 10 ** 9), random.randint(0, 10 ** 9), random.randint(0, 10 ** 9)))
print(chr(10).join(lines))
