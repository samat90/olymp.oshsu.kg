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
    n = r.randint(1, 5) if t <= 3 else (300 if t == 10 else r.randint(50, 300)); m = r.randint(1, 5) if t <= 3 else (300 if t == 10 else r.randint(50, 300))
    if t == 0: m = r.randint(1, 8)
    x = [r.randint(0, 1) for _ in range(m)]; consistent = t % 2 == 0 or t == 0 and r.random() < 0.5
    o = ["%d %d" % (n, m)]
    for _ in range(n):
        row = [r.randint(0, 1) if r.random() < 0.5 else 0 for _ in range(m)]
        b = sum(a*c for a, c in zip(row, x)) % 2
        if not consistent and r.random() < 0.3: b ^= 1
        o.append("".join(map(str, row)) + " %d" % b)
    return "\n".join(o) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2105 * 1000 + t)
    sys.stdout.write(gen(r, t))
