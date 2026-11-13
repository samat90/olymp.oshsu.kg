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
    n = r.randint(1, 8) if t <= 3 else (40 if t == 10 else r.randint(25, 40))
    H = 6 if t <= 3 else (30 if t in (4, 5, 6) else 10**9)
    a = [r.randint(1, H) for _ in range(n)]
    if t == 0: S = r.randint(0, 20)
    else:
        S = sum(x for x in a if r.random() < 0.5)
        if t == 1: S = 0
    return "%d %d\n" % (n, S) + " ".join(map(str, a)) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2112 * 1000 + t)
    sys.stdout.write(gen(r, t))
