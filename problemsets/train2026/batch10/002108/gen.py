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
    n = r.randint(1, 6) if t <= 3 else (1000 if t == 10 else r.randint(100, 1000)); m = r.randint(1, 6) if t <= 3 else (1000 if t == 10 else r.randint(100, 1000))
    p = r.choice([0.0, 0.05, 0.1, 0.2]) if t > 3 else r.choice([0.1, 0.2, 0.3])
    g = ["".join('#' if r.random() < p else '.' for _ in range(m)) for _ in range(n)]
    if t != 5 and t != 0:
        g[0] = '.' + g[0][1:]; g[-1] = g[-1][:-1] + '.'
    return "%d %d\n" % (n, m) + "\n".join(g) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2108 * 1000 + t)
    sys.stdout.write(gen(r, t))
