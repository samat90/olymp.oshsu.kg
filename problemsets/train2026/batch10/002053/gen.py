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
    n = N(r, t, 4, 100000)
    H = 2 if t <= 4 else 10**9
    if t == 0: H = 3
    while True:
        a = [r.randint(0, H) for _ in range(n)]
        if t in (5, 6): a = [1]*n if t == 5 else [1]*(n-1) + [5]
        if sum(a) > 0: break
    return "%d\n" % n + " ".join(map(str, a)) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2053 * 1000 + t)
    sys.stdout.write(gen(r, t))
