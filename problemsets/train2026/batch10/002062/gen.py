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
    m = r.randint(1, 8) if t == 0 else ([1, 2, 5, 10, 12, 15, 17, 18, 19, 20][t-1])
    T_ = r.randint(1, m*(m+1)//2)
    return "%d %d\n" % (m, T_)

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2062 * 1000 + t)
    sys.stdout.write(gen(r, t))
