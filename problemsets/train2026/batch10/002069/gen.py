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
    n = r.randint(3, 6) if t <= 3 else r.randint(30, 40); m = r.randint(3, 6) if t <= 3 else r.randint(30, 40)
    if t == 10: n = m = 40
    k = r.randint(0, 6) if t <= 3 else r.randint(50, 100)
    p = r.choice([0.2, 0.35, 0.5])
    return "%d %d %d\n" % (n, m, k) + "".join("".join('#' if r.random() < p else '.' for _ in range(m)) + "\n" for _ in range(n))

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2069 * 1000 + t)
    sys.stdout.write(gen(r, t))
