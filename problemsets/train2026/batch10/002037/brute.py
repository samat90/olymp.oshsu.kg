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
    v = list(map(int, s.split())); n = v[0]
    P = [(v[1+2*i], v[2+2*i]) for i in range(n)]
    best = min(n, 2)
    for i in range(n):
        for j in range(i+1, n):
            c = sum(1 for k in range(n) if (P[j][0]-P[i][0])*(P[k][1]-P[i][1]) == (P[j][1]-P[i][1])*(P[k][0]-P[i][0]))
            best = max(best, c)
    return best

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
