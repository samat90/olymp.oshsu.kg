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
    v = list(map(int, s.split())); n, k = v[0], v[1]; A = [v[2+i*n:2+(i+1)*n] for i in range(n)]; P = 10**9 + 7
    def mul(X, Y):
        Yt = list(zip(*Y))
        return [[sum(a*b for a, b in zip(row, col)) % P for col in Yt] for row in X]
    R = [[int(i == j) for j in range(n)] for i in range(n)]
    while k:
        if k & 1: R = mul(R, A)
        A = mul(A, A); k >>= 1
    return mat_text(R)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
