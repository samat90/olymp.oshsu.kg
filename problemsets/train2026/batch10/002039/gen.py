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
    M = 6 if t <= 5 else 10**9
    if t == 0: M = 6
    o = []
    if t == 10:
        return "-1000000000 -1000000000 1000000000 1000000000\n-1000000000 -1000000000 1000000000 1000000000\n"
    for _ in range(2):
        x1 = r.randint(-M, M-1); x2 = r.randint(x1+1, M); y1 = r.randint(-M, M-1); y2 = r.randint(y1+1, M)
        o.append("%d %d %d %d" % (x1, y1, x2, y2))
    return "\n".join(o) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2039 * 1000 + t)
    sys.stdout.write(gen(r, t))
