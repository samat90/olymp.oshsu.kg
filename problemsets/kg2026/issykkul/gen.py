"""gen.py q cmax mode(rand/circle/lake/line/vertical/spiral) qfrac seed

qfrac: share of questions ('?' and 'A') among the events.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, write  # noqa: E402

q, cmax, mode, qfrac, s = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], float(sys.argv[4]), sys.argv[5]
seed(s)
pts = []
lines = [str(q)]


def clamp(v):
    return max(-cmax, min(cmax, v))


def new_point(i):
    if mode == 'circle':
        a = random.random() * 2 * math.pi
        r = cmax * (0.999 + 0.001 * random.random())
        return clamp(int(r * math.cos(a))), clamp(int(r * math.sin(a)))
    if mode == 'lake':  # an ellipse like Issyk-Kul: 180 x 60, growing outwards over time
        a = random.random() * 2 * math.pi
        r = cmax * min(1.0, 0.05 + i / q) * (0.9 + 0.1 * random.random())
        return clamp(int(r * math.cos(a))), clamp(int(r / 3 * math.sin(a)))
    if mode == 'line':
        t = random.randint(-cmax // 3, cmax // 3)
        return clamp(t * 3 // 1), clamp(-t + 7)
    if mode == 'vertical':
        return 5, random.randint(-cmax, cmax)
    if mode == 'spiral':
        a = i * 0.7
        r = cmax * (i + 1) / q
        return clamp(int(r * math.cos(a))), clamp(int(r * math.sin(a)))
    return random.randint(-cmax, cmax), random.randint(-cmax, cmax)


def question():
    c = random.random()
    if c < 0.1:
        return 'A'
    if pts and c < 0.4:
        a, b = random.choice(pts), random.choice(pts)
        if (a[0] + b[0]) % 2 == 0 and (a[1] + b[1]) % 2 == 0:
            return '? %d %d' % ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)
        return '? %d %d' % a
    if pts and c < 0.6:
        a = random.choice(pts)
        return '? %d %d' % (clamp(a[0] + random.randint(-2, 2)), clamp(a[1] + random.randint(-2, 2)))
    x, y = new_point(len(pts))
    return '? %d %d' % (clamp(x + random.randint(-3, 3)), clamp(y + random.randint(-3, 3)))


static = qfrac < 0  # all buoys first, questions afterwards
qfrac = abs(qfrac)
if static:
    adds = max(1, int(q * (1 - qfrac)))
    for i in range(adds):
        p = new_point(i)
        pts.append(p)
        lines.append('+ %d %d' % p)
    lines += [question() for _ in range(q - adds)]
for i in range(0 if static else q):
    if i > 0 and random.random() < qfrac:
        lines.append(question())
    else:
        p = new_point(i)
        pts.append(p)
        lines.append('+ %d %d' % p)
write(lines)
