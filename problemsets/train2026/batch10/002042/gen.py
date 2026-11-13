import sys, random
from math import *
from itertools import *
from functools import *
from collections import *
from bisect import *
import heapq
from fractions import Fraction
import builtins, re
pow = builtins.pow
sys.setrecursionlimit(1000000)
def mat_text(a): return "\n".join(" ".join(map(str, r)) for r in a)

def N(r, t, tiny, big):
    if t == 0: return r.randint(1, tiny)
    if t == 10: return big
    if t <= 3: return r.randint(1, tiny * 2)
    return max(1, big * t * t // 100)

def star(r, n, R):
    from math import gcd
    from functools import cmp_to_key
    dirs = {(1,0),(0,1),(-1,0),(0,-1)}
    tries = 0
    while len(dirs) < n and tries < 100000:
        tries += 1
        dx, dy = r.randint(-R, R), r.randint(-R, R)
        if dx == 0 and dy == 0: continue
        g = gcd(abs(dx), abs(dy)); dirs.add((dx // g, dy // g))
    pts = []
    for dx, dy in dirs:
        m = max(abs(dx), abs(dy))
        k = r.randint(1, max(1, R // m))
        pts.append((dx * k, dy * k))
    def half(p): return 0 if (p[1] > 0 or (p[1] == 0 and p[0] > 0)) else 1
    def cmp(a, b):
        ha, hb = half(a), half(b)
        if ha != hb: return ha - hb
        c = a[0] * b[1] - a[1] * b[0]
        return -1 if c > 0 else (1 if c < 0 else 0)
    pts.sort(key=cmp_to_key(cmp))
    return pts

def gen(r, t):
    n = max(3, N(r, t, 6, 100000))
    R = 6 if t <= 3 else (60 if t < 5 else 10**6)
    if t == 0: R = 5
    pts = star(r, n, R)
    if r.random() < 0.5: pts.reverse()
    return "%d\n" % len(pts) + "".join("%d %d\n" % p for p in pts)

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2042 * 1000 + t)
    sys.stdout.write(gen(r, t))
