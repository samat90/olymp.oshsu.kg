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
    tot = 0
    for a, b, c in combinations(P, 3):
        for o, p, q in ((a,b,c),(b,a,c),(c,a,b)):
            if (p[0]-o[0])*(q[0]-o[0]) + (p[1]-o[1])*(q[1]-o[1]) == 0:
                tot += 1
    return tot

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
