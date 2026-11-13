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
    v = list(map(int, s.split())); d, Nn = v[0], v[1]; a = v[2:2+d]; c = v[2+d:2+2*d]; P = 10**9 + 7
    if Nn < d: return a[Nn] % P
    M = [[0]*d for _ in range(d)]
    M[0] = c[:]
    for i in range(1, d): M[i][i-1] = 1
    def mul(X, Y):
        return [[sum(X[i][k]*Y[k][j] for k in range(d)) % P for j in range(d)] for i in range(d)]
    R = [[int(i == j) for j in range(d)] for i in range(d)]; e = Nn - d + 1
    while e:
        if e & 1: R = mul(R, M)
        M = mul(M, M); e >>= 1
    vec = a[::-1]   # a_{d-1}, ..., a_0
    return sum(R[0][j]*vec[j] for j in range(d)) % P

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
