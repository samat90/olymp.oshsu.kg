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
    cr = lambda o,a,b: (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    def onseg(p, a, b): return cr(a,b,p) == 0 and min(a[0],b[0]) <= p[0] <= max(a[0],b[0]) and min(a[1],b[1]) <= p[1] <= max(a[1],b[1])
    def intri(p, a, b, c):
        d = [cr(a,b,p), cr(b,c,p), cr(c,a,p)]
        return cr(a,b,c) != 0 and not (min(d) < 0 and max(d) > 0)
    cnt = 0
    for i, p in enumerate(P):
        O = P[:i] + P[i+1:]
        inside = any(onseg(p, a, b) for a, b in combinations(O, 2)) or any(intri(p, a, b, c) for a, b, c in combinations(O, 3))
        if not inside: cnt += 1
    return cnt

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
