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
    T_ = N(r, t, 6, 100000)
    H = 12 if t <= 3 else 10**18
    o = [str(T_)]
    for _ in range(T_):
        n = r.randint(1, H); k = r.randint(1, max(1, min(H, n if r.random() < 0.5 else 10**9)))
        if t > 3 and r.random() < 0.3: n = (k+1) * r.randint(1, max(1, H // (k+1)))
        o.append("%d %d" % (n, k))
    return "\n".join(o) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2050 * 1000 + t)
    sys.stdout.write(gen(r, t))
