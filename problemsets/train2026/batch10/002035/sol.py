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
    for i in range(n):
        cnt = {}
        for j in range(n):
            if i == j: continue
            dx, dy = P[j][0]-P[i][0], P[j][1]-P[i][1]
            g = gcd(abs(dx), abs(dy)); d = (dx//g, dy//g)
            cnt[d] = cnt.get(d, 0) + 1
        for (dx, dy), c in cnt.items():
            tot += c * cnt.get((-dy, dx), 0)
    return tot

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
