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
    n = N(r, t, 6, 500)
    M = 3 if t <= 3 else (12 if t < 8 else 10**9)
    n = min(n, (2*M+1)**2)
    S = set()
    if t >= 8:
        # many points on a few lines
        while len(S) < n:
            k = r.randint(-1000, 1000); a = r.choice([(1,1),(2,3),(1,0),(5,-7)])
            S.add((k*a[0]*1000, k*a[1]*1000 + r.choice([0,0,0,5])))
    else:
        while len(S) < n: S.add((r.randint(-M, M), r.randint(-M, M)))
    L = list(S); r.shuffle(L)
    return "%d\n" % len(L) + "".join("%d %d\n" % p for p in L)

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2037 * 1000 + t)
    sys.stdout.write(gen(r, t))
