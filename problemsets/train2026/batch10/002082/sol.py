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
    v = list(map(int, s.split())); n, D = v[0], v[1]; w = v[2:2+n]
    def ok(c):
        days = 1; cur = 0
        for x in w:
            if cur + x > c: days += 1; cur = 0
            cur += x
        return days <= D
    lo, hi = max(w), sum(w)
    while lo < hi:
        m = (lo + hi) // 2
        if ok(m): hi = m
        else: lo = m + 1
    return lo

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
