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
    S = set(P); c = 0
    for (x1, y1) in P:
        for (x2, y2) in P:
            if (x1, y1) == (x2, y2): continue
            dx, dy = x2-x1, y2-y1
            if (x2-dy, y2+dx) in S and (x1-dy, y1+dx) in S: c += 1
    return c // 4

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
