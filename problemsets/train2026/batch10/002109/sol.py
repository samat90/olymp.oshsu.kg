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
    v = list(map(int, s.split())); n, k = v[0], v[1]; a = [v[2+i*n:2+(i+1)*n] for i in range(n)]
    lo, hi = a[0][0], a[n-1][n-1]
    def cnt(x):
        c = 0; j = n-1
        for i in range(n):
            while j >= 0 and a[i][j] > x: j -= 1
            c += j + 1
        return c
    while lo < hi:
        mid = (lo + hi) // 2
        if cnt(mid) >= k: hi = mid
        else: lo = mid + 1
    return lo

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
