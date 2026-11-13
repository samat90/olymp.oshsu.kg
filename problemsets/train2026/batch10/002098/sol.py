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
    v = list(map(int, s.split())); n, m = v[0], v[1]
    P = [[0]*(m+1) for _ in range(n+1)]; p = 2
    for i in range(1, n+1):
        run = 0; Pi = P[i]; Pp = P[i-1]
        for j in range(1, m+1):
            run += v[p]; p += 1; Pi[j] = Pp[j] + run
    q = v[p]; p += 1; o = []
    for _ in range(q):
        r1, c1, r2, c2 = v[p:p+4]; p += 4
        o.append(P[r2][c2] - P[r1-1][c2] - P[r2][c1-1] + P[r1-1][c1-1])
    return "\n".join(map(str, o))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
