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
    n = r.randint(1, 6) if t <= 3 else (700 if t == 10 else r.randint(100, 700)); m = r.randint(1, 6) if t <= 3 else (700 if t == 10 else r.randint(100, 700))
    p = r.choice([0.3, 0.45, 0.6, 0.5])
    return "%d %d\n" % (n, m) + "\n".join("".join('1' if r.random() < p else '0' for _ in range(m)) for _ in range(n)) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2102 * 1000 + t)
    sys.stdout.write(gen(r, t))
