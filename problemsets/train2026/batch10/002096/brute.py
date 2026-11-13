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
    R = [[int(i == j) for j in range(n)] for i in range(n)]
    for _ in range(k):
        R = [[sum(R[i][x]*A[x][j] for x in range(n)) % P for j in range(n)] for i in range(n)]
    return mat_text(R)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
