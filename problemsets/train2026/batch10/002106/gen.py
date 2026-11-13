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
    T_ = N(r, t, 3, 1000); out = [str(T_)]
    for _ in range(T_):
        dg = list(range(1, 10)); r.shuffle(dg)
        rows = r.sample([0,1,2], 3); cols = r.sample([0,1,2], 3)
        R = [3*b + x for b in r.sample([0,1,2], 3) for x in r.sample([0,1,2], 3)]
        C = [3*b + x for b in r.sample([0,1,2], 3) for x in r.sample([0,1,2], 3)]
        g = [[dg[(3*(i % 3) + i // 3 + j) % 9] for j in range(9)] for i in R]
        g = [[row[j] for j in C] for row in g]
        p = r.choice([0.3, 0.6, 0.9])
        g = [[x if r.random() > p else 0 for x in row] for row in g]
        if r.random() < 0.5:
            for _ in range(r.randint(1, 2)): g[r.randint(0, 8)][r.randint(0, 8)] = r.randint(1, 9)
        out += ["".join(map(str, row)) for row in g]
    return "\n".join(out) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2106 * 1000 + t)
    sys.stdout.write(gen(r, t))
