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


def solve(s):
    v = list(map(int, s.split())); n = v[0]
    P = [(v[1+2*i], v[2+2*i]) for i in range(n)]
    best = 0
    for q in combinations(P, 4):
        xs = sorted({p[0] for p in q}); ys = sorted({p[1] for p in q})
        if len(xs) == 2 and len(ys) == 2 and {(x, y) for x in xs for y in ys} == set(q):
            a = (xs[1]-xs[0]) * (ys[1]-ys[0])
            if best == 0 or a < best: best = a
    return best

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
