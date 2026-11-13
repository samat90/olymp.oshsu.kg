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
    v = s.split(); n, m = int(v[0]), int(v[1]); g = v[2:2+n]
    def f(i, j):
        if g[i][j] == '#': return 0
        if i == n-1 and j == m-1: return 1
        return (f(i+1, j) if i+1 < n else 0) + (f(i, j+1) if j+1 < m else 0)
    return f(0, 0) % (10**9 + 7)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
