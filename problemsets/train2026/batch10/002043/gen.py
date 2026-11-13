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
    n = max(2, N(r, t, 6, 50000))
    M = 4 if t <= 3 else (200 if t >= 9 else 10**9)
    if t == 0: M = 4
    n = min(n, (2*M+1)**2)
    S = set()
    while len(S) < n: S.add((r.randint(-M, M), r.randint(-M, M)))
    L = list(S); r.shuffle(L)
    return "%d\n" % n + "".join("%d %d\n" % p for p in L)

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2043 * 1000 + t)
    sys.stdout.write(gen(r, t))
