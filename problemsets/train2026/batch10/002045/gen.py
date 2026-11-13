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
    n = N(r, t, 4, 100000)
    M = 12 if t <= 3 else 10**9
    if t == 0: M = 10
    H = 5 if t <= 3 else 10**9
    o = [str(n)]
    for _ in range(n):
        if t > 3:
            l = r.randint(0, M-1); w = r.randint(1, max(1, min(M-l, M // max(1, n // 10 or 1))))
            a, b = l, min(M, l+w)
        else:
            a = r.randint(0, M-1); b = r.randint(a+1, M)
        o.append("%d %d %d" % (a, b, r.randint(1, H)))
    return "\n".join(o) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2045 * 1000 + t)
    sys.stdout.write(gen(r, t))
