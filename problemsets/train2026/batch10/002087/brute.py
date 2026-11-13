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


def solve(s):
    a, b = s.split(); n, m = len(a), len(b); best = None
    for pos in combinations(range(n+m), n):
        P = set(pos); i = j = 0; res = []
        for k in range(n+m):
            if k in P: res.append(a[i]); i += 1
            else: res.append(b[j]); j += 1
        res = "".join(res)
        if best is None or res < best: best = res
    return best

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
