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


def gen(r, t):
    n = N(r, t, 4, 400)
    M = 5 if t <= 3 else 10**9
    if t == 0: M = 5
    o = [str(n)]
    for _ in range(n):
        if t <= 3 or t == 0: 
            x1 = r.randint(-M, M-1); x2 = r.randint(x1+1, M); y1 = r.randint(-M, M-1); y2 = r.randint(y1+1, M)
        else:
            cx, cy = r.randint(-M, M), r.randint(-M, M); w = r.randint(1, M//3); h = r.randint(1, M//3)
            x1, x2, y1, y2 = max(-M, cx-w), min(M, cx+w), max(-M, cy-h), min(M, cy+h)
            if x1 >= x2: x1, x2 = -M, -M+1
            if y1 >= y2: y1, y2 = -M, -M+1
        o.append("%d %d %d %d" % (x1, y1, x2, y2))
    return "\n".join(o) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2040 * 1000 + t)
    sys.stdout.write(gen(r, t))
