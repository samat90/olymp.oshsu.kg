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
    n = r.randint(1, 4) * 2 if t <= 3 else (200000 if t == 10 else r.randint(5, 100000) * 2)
    q = N(r, t, 6, 200000)
    o = ["%d %d" % (n, q)]
    for _ in range(q):
        o.append("2" if r.random() < 0.4 else "1 %d" % r.randint(-n, n))
    return "\n".join(o) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2075 * 1000 + t)
    sys.stdout.write(gen(r, t))
