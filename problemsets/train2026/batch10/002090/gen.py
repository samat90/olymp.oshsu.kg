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
    n = r.randint(1, 7) if t <= 3 else r.randint(12, 20)
    if t == 10: n = 20
    return "%d %d\n" % (n, r.randint(1, factorial(n)))

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2090 * 1000 + t)
    sys.stdout.write(gen(r, t))
