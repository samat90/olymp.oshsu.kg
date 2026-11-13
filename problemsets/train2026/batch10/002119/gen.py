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
    n = r.randint(1, 6) if t <= 3 else (12 if t >= 9 else r.randint(8, 12))
    pairs = [(i, j) for i in range(1, n+1) for j in range(i+1, n+1)]
    p = r.choice([0.2, 0.4, 0.6, 0.8])
    E = [e for e in pairs if r.random() < p]
    return "%d %d\n" % (n, len(E)) + "".join("%d %d\n" % e for e in E)

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2119 * 1000 + t)
    sys.stdout.write(gen(r, t))
