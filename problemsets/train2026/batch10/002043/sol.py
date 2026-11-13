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
    P = sorted((v[1+2*i], v[2+2*i]) for i in range(n))
    best = (P[0][0]-P[1][0])**2 + (P[0][1]-P[1][1])**2
    for i in range(1, n):
        j = i - 1
        xi, yi = P[i]
        while j >= 0 and (xi - P[j][0])**2 < best:
            d = (xi-P[j][0])**2 + (yi-P[j][1])**2
            if d < best: best = d
            j -= 1
    return best

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
