"""gen.py q maxV seed"""
import random
import sys

q, M, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
random.seed(s * 17 + q)
out = []
for _ in range(q):
    r = random.random()
    if r < 0.6:
        a, b = random.randint(1, M), random.randint(1, M)
    elif r < 0.8:
        a = random.randint(M * 9 // 10, M)
        b = random.randint(M * 9 // 10, M)
    elif r < 0.9:
        a, b = random.randint(1, 30), random.randint(1, M)
    else:
        a = b = random.randint(1, M)
    if random.random() < 0.5:
        a, b = b, a
    out.append('%d %d' % (a, b))
print(q)
print('\n'.join(out))
