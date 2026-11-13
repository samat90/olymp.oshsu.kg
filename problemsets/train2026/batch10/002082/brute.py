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
    c = max(w)
    while True:
        days = 1; cur = 0
        for x in w:
            if cur + x > c: days += 1; cur = 0
            cur += x
        if days <= D: return c
        c += 1

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
