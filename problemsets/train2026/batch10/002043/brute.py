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
    return min((a[0]-b[0])**2 + (a[1]-b[1])**2 for a, b in combinations(P, 2))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
