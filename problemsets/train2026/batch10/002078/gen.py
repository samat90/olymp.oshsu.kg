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
    n = r.randint(1, 5) if t <= 3 else (300 if t == 10 else r.randint(50, 300))
    vals = [0, 0, 2, 2, 4, 8] if t > 2 else [0, 2, 2, 4]
    g = [[r.choice(vals) for _ in range(n)] for _ in range(n)]
    return "%d\n" % n + "".join(" ".join(map(str, row)) + "\n" for row in g) + r.choice("LRUD") + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2078 * 1000 + t)
    sys.stdout.write(gen(r, t))
