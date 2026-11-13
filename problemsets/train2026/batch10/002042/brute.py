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

def solve(s):
    v = list(map(int, s.split())); n = v[0]
    P = [(v[1+2*i], v[2+2*i]) for i in range(n)]
    def onb(x, y):
        for i in range(n):
            a, b = P[i], P[(i+1)%n]
            if (b[0]-a[0])*(y-a[1]) == (b[1]-a[1])*(x-a[0]) and min(a[0],b[0]) <= x <= max(a[0],b[0]) and min(a[1],b[1]) <= y <= max(a[1],b[1]): return True
        return False
    def inside(x, y):
        c = False
        for i in range(n):
            a, b = P[i], P[(i+1)%n]
            if (a[1] > y) != (b[1] > y):
                xi = Fraction(b[0]-a[0], 1) * Fraction(y-a[1], b[1]-a[1]) + a[0]
                if x < xi: c = not c
        return c
    xs = [p[0] for p in P]; ys = [p[1] for p in P]
    cnt = 0
    for x in range(min(xs), max(xs)+1):
        for y in range(min(ys), max(ys)+1):
            if not onb(x, y) and inside(x, y): cnt += 1
    return cnt

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
