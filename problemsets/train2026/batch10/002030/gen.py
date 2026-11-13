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
    T_ = N(r, t, 5, 100000) if t else r.randint(1, 3)
    M = 3 if t in (0, 1, 2) else (50 if t < 6 else 10**6)
    out = [str(T_)]
    for _ in range(T_):
        out.append(" ".join(str(r.randint(-M, M)) for _ in range(6)))
    return "\n".join(out) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2030 * 1000 + t)
    sys.stdout.write(gen(r, t))
