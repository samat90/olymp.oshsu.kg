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
    n, h = map(int, s.split()); P = 10**9 + 7
    f = [1] + [0]*n   # f[k] — число деревьев из k узлов высоты ≤ текущей
    for _ in range(h):
        g = [0]*(n+1); g[0] = 1
        for k in range(1, n+1):
            g[k] = sum(f[l] * f[k-1-l] for l in range(k)) % P
        f = g
    return f[n]

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
