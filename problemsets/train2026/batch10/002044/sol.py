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
    S = set(P); best = 0
    for i in range(n):
        for j in range(i+1, n):
            if P[i][0] != P[j][0] and P[i][1] != P[j][1] and (P[i][0], P[j][1]) in S and (P[j][0], P[i][1]) in S:
                a = abs(P[i][0]-P[j][0]) * abs(P[i][1]-P[j][1])
                if best == 0 or a < best: best = a
    return best

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
