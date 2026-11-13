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
    n = r.randint(1, 4) if t <= 3 else (200 if t == 10 else r.randint(30, 200)); m = r.randint(1, 4) if t <= 3 else (200 if t == 10 else r.randint(30, 200))
    q = r.randint(1, 8) if t <= 3 else (100000 if t == 10 else r.randint(10, 100000))
    return "%d %d\n" % (n, m) + mat_text([[r.randint(0, 99 if t <= 5 else 10**9) for _ in range(m)] for _ in range(n)]) + "\n" + "".join(r.choice("RHVT") for _ in range(q)) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2095 * 1000 + t)
    sys.stdout.write(gen(r, t))
