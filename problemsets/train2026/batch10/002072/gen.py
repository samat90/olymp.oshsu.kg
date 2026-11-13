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
    W = r.randint(1, 5) if t <= 3 else r.randint(1, 10**9); H = r.randint(1, 5) if t <= 3 else r.randint(1, 10**9)
    T_ = r.randint(0, 40) if t <= 3 else r.randint(0, 10**18)
    return "%d %d %d %d %d %d %d\n" % (W, H, r.randint(0, W), r.randint(0, H), r.choice([-1, 1]), r.choice([-1, 1]), T_)

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2072 * 1000 + t)
    sys.stdout.write(gen(r, t))
