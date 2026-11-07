"""gen.py n R mode(rand/disk/circle/fan/rect/line) seed: distinct integer points"""
import math
import random
import sys

n, R, mode, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
random.seed(s * 1009 + n)
pts = set()


def circle_points(r):
    res = []
    for x in range(-r, r + 1):
        y2 = r * r - x * x
        y = math.isqrt(y2)
        if y * y == y2:
            res += [(x, y), (x, -y)]
    return list(set(res))


if mode == 'circle':  # R with many representations as a sum of two squares, plus random inner points
    ring = circle_points(R)
    random.shuffle(ring)
    for q in ring[:max(2, min(len(ring), n // 2))]:
        pts.add(q)
    while len(pts) < n:
        x, y = random.randint(-R, R), random.randint(-R, R)
        if x * x + y * y < R * R:
            pts.add((x, y))
elif mode == 'fan':  # one point and many points on a short arc around it: many farthest pairs
    pts.add((0, 0))
    r = 5 ** 6
    arc = [(x, y) for x, y in circle_points(r) if x > 0 and abs(y) * 2 < x]
    random.shuffle(arc)
    for q in arc[:n - 1]:
        pts.add(q)
    while len(pts) < n:
        x, y = random.randint(0, r // 2), random.randint(-r // 8, r // 8)
        pts.add((x, y))
elif mode == 'rect':
    lo = int(n ** 0.5) + 2
    a, b = random.randint(min(lo, R), max(lo, R)), random.randint(min(lo, R), max(lo, R))
    for q in ((0, 0), (a, 0), (0, b), (a, b)):
        pts.add(q)
    while len(pts) < n:
        pts.add((random.randint(0, a), random.randint(0, b)))
elif mode == 'line':
    dx, dy = random.randint(1, 5), random.randint(-5, 5)
    t = list(range(-R // 6, R // 6))
    for v in random.sample(t, min(n, len(t))):
        pts.add((v * dx // 1 if abs(v * dx) <= R else v, v * dy if abs(v * dy) <= R else 0))
    while len(pts) < n:
        pts.add((random.randint(-R, R), random.randint(-R, R)))
elif mode == 'disk':
    while len(pts) < n:
        a = random.random() * 2 * math.pi
        rr = R * math.sqrt(random.random())
        pts.add((int(rr * math.cos(a)), int(rr * math.sin(a))))
else:
    while len(pts) < n:
        pts.add((random.randint(-R, R), random.randint(-R, R)))
pts = list(pts)[:n]
random.shuffle(pts)
print(len(pts))
print('\n'.join('%d %d' % q for q in pts))
