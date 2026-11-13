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
    v = list(map(int, s.split())); n, m = v[0], v[1]; a = [v[2+i*m:2+(i+1)*m] for i in range(n)]
    best = -10**18
    for top in range(n):
        col = [0]*m
        for bot in range(top, n):
            cur = None; run = 0
            for j in range(m):
                col[j] += a[bot][j]
                run = col[j] if run <= 0 else run + col[j]
                if run > best: best = run
    return best

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
