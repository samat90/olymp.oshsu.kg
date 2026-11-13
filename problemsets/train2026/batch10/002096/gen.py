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
    n = r.randint(1, 3) if t <= 3 else (30 if t == 10 else r.randint(5, 30))
    k = r.randint(0, 12) if t <= 3 else r.randint(0, 10**18)
    if t == 10: k = 10**18
    P = 10**9 + 7
    return "%d %d\n" % (n, k) + mat_text([[r.randint(0, P-1) if t > 3 else r.randint(0, 3) for _ in range(n)] for _ in range(n)]) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2096 * 1000 + t)
    sys.stdout.write(gen(r, t))
