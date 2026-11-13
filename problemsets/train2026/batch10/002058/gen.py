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
    T_ = N(r, t, 5, 100000)
    H = 8 if t <= 3 else 10**6
    o = [str(T_)]
    for _ in range(T_):
        while True:
            x, y = r.randint(0, H), r.randint(0, H)
            if (x, y) != (0, 0): break
        o.append("%d %d" % (x, y))
    return "\n".join(o) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2058 * 1000 + t)
    sys.stdout.write(gen(r, t))
