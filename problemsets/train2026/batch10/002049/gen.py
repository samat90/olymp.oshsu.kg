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
    H = 4 if t <= 3 else 10**9
    a = [r.randint(0, H) for _ in range(n)]
    if t >= 6 and t % 2 == 0 and n > 2:
        x = 0
        for v in a[:-1]: x ^= v
        a[-1] = x
    return "%d\n" % n + " ".join(map(str, a)) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2049 * 1000 + t)
    sys.stdout.write(gen(r, t))
