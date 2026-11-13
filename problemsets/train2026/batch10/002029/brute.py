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
    a = list(map(int, s.split()))
    P = [(a[0],a[1]),(a[2],a[3]),(a[4],a[5])]
    d = lambda p,q: (p[0]-q[0])**2 + (p[1]-q[1])**2
    x, y, z = d(P[0],P[1]), d(P[1],P[2]), d(P[2],P[0])
    q = 2*(x*y+y*z+z*x) - x*x - y*y - z*z
    return isqrt(q // 4)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
