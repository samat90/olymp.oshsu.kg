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
    n = r.randint(1, 5) if t <= 3 else (500 if t == 10 else r.randint(50, 500))
    step = 3 if t <= 3 else 4000
    a = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            base = max(a[i-1][j] if i else 0, a[i][j-1] if j else 0)
            a[i][j] = base + r.randint(0, step)
    k = r.randint(1, n*n)
    return "%d %d\n" % (n, k) + mat_text(a) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2109 * 1000 + t)
    sys.stdout.write(gen(r, t))
