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
    def f(i, j):
        if i == n-1 and j == m-1: return a[i][j]
        best = []
        if i+1 < n: best.append(f(i+1, j))
        if j+1 < m: best.append(f(i, j+1))
        return a[i][j] + min(best)
    return f(0, 0)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
