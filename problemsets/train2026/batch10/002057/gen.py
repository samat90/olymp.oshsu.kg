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
    n = max(1, N(r, t, 6, 100000))
    m = 0 if n == 1 else r.randint(0, min(2*n, 200000, n*(n-1)//2)) if t <= 3 else min(200000, 2*n)
    E = set()
    if n > 1:
        while len(E) < m:
            u = r.randint(1, n-1); v = r.randint(u+1, min(n, u + (3 if t > 3 else n)))
            E.add((u, v))
    E = list(E); r.shuffle(E)
    return "%d %d\n" % (n, len(E)) + "".join("%d %d\n" % e for e in E)

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2057 * 1000 + t)
    sys.stdout.write(gen(r, t))
