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
    B = [v[1+3*i:4+3*i] for i in range(n)]
    mx = max(b[1] for b in B)
    res = []; cur = 0
    for x in range(0, mx+1):
        h = max([b[2] for b in B if b[0] <= x < b[1]], default=0)
        if h != cur: res.append((x, h)); cur = h
    return "%d\n" % len(res) + "\n".join("%d %d" % p for p in res)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
