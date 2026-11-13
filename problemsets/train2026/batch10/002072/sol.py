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
    w, h, x, y, dx, dy, t = map(int, s.split())
    def f(p, d, L):
        m = (p + d * t) % (2 * L)
        return m if m <= L else 2 * L - m
    return "%d %d" % (f(x, dx, w), f(y, dy, h))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
