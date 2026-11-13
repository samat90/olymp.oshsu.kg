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
    v = list(map(int, s.split())); n = v[0]; P = 10**9 + 7
    a = [[x % P for x in v[1+i*n:1+(i+1)*n]] for i in range(n)]; det = 1
    for c in range(n):
        piv = next((r_ for r_ in range(c, n) if a[r_][c]), None)
        if piv is None: return 0
        if piv != c: a[piv], a[c] = a[c], a[piv]; det = -det
        det = det * a[c][c] % P; inv = pow(a[c][c], P-2, P)
        for r_ in range(c+1, n):
            f = a[r_][c] * inv % P
            if f:
                rc = a[c]; rr = a[r_]
                for k in range(c, n): rr[k] = (rr[k] - f * rc[k]) % P
    return det % P

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
