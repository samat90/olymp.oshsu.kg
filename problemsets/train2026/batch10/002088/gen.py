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
    n = N(r, t, 6, 2000)
    if t == 0: n = r.randint(1, 6)
    a = list(range(1, n+1)); r.shuffle(a)
    k = r.randint(0, 6) if t <= 3 else r.choice([r.randint(0, 100), r.randint(0, 10**9), r.randint(0, n*n//4)])
    return "%d %d\n" % (n, k) + " ".join(map(str, a)) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2088 * 1000 + t)
    sys.stdout.write(gen(r, t))
