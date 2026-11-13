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
    P = [[0]*(m+1) for _ in range(n+1)]
    for i in range(n):
        for j in range(m): P[i+1][j+1] = P[i][j+1] + P[i+1][j] - P[i][j] + a[i][j]
    return max(P[r2][c2] - P[r1][c2] - P[r2][c1] + P[r1][c1] for r1 in range(n) for r2 in range(r1+1, n+1) for c1 in range(m) for c2 in range(c1+1, m+1))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
