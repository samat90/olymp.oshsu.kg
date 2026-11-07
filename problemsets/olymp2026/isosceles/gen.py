"""gen.py n R mode(rand/grid/sym/line/circle) seed: distinct points"""
import math
import random
import sys

n, R, mode, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
random.seed(s * 2713 + n)
pts = set()
if mode == 'grid':
    cells = [(x, y) for x in range(R) for y in range(R)]
    random.shuffle(cells)
    pts = set(cells[:n])
elif mode == 'sym':  # symmetric around a few centres: many equal distances and midpoints
    cs = [(random.randint(-R // 2, R // 2), random.randint(-R // 2, R // 2)) for _ in range(3)]
    while len(pts) < n:
        cx, cy = random.choice(cs)
        dx, dy = random.randint(-R // 2, R // 2), random.randint(-R // 2, R // 2)
        pts.add((cx + dx, cy + dy))
        if len(pts) < n:
            pts.add((cx - dx, cy - dy))
        if len(pts) < n and random.random() < 0.5:
            pts.add((cx - dy, cy + dx))
elif mode == 'line':
    while len(pts) < n:
        t = random.randint(-10 ** 6, 10 ** 6)
        pts.add((t * 3, t * 2) if random.random() < 0.7 else (random.randint(-R, R), random.randint(-R, R)))
elif mode == 'circle':
    ring = []
    for x in range(-R, R + 1):
        y2 = R * R - x * x
        y = math.isqrt(y2)
        if y * y == y2:
            ring += [(x, y), (x, -y)]
    pts = set(ring[:n // 2]) | {(0, 0)}
    while len(pts) < n:
        pts.add((random.randint(-R, R), random.randint(-R, R)))
else:
    while len(pts) < n:
        pts.add((random.randint(-R, R), random.randint(-R, R)))
pts = list(pts)[:n]
random.shuffle(pts)
print(len(pts))
print('\n'.join('%d %d' % q for q in pts))
