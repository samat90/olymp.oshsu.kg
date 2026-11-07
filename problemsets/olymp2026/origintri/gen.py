"""gen.py n R seed: no two stars on one line through the origin"""
import math
import random
import sys

n, R, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
random.seed(s * 4111 + n)
mode = random.choice(['square', 'disk', 'halfish', 'clusters'])
used = set()
pts = []
centers = [random.random() * 2 * math.pi for _ in range(5)]
tries = 0
while len(pts) < n and tries < 50 * n:
    tries += 1
    if mode == 'disk':
        a = random.random() * 2 * math.pi
        r = R * math.sqrt(random.random())
        x, y = int(r * math.cos(a)), int(r * math.sin(a))
    elif mode == 'halfish':  # most stars in one half-plane: few good triangles
        a = random.random() * math.pi * 1.1 - 0.05
        r = R * random.random()
        x, y = int(r * math.cos(a)), int(r * math.sin(a))
    elif mode == 'clusters':
        a = random.choice(centers) + random.gauss(0, 0.2)
        r = R * random.random()
        x, y = int(r * math.cos(a)), int(r * math.sin(a))
    else:
        x, y = random.randint(-R, R), random.randint(-R, R)
    if x == 0 and y == 0:
        continue
    g = math.gcd(x, y)
    key = (x // g, y // g)
    if key in used or (-key[0], -key[1]) in used:
        continue
    used.add(key)
    pts.append((x, y))
print(len(pts))
print('\n'.join('%d %d' % q for q in pts))
