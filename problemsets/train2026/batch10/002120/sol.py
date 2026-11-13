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
    n, k = map(int, s.split()); a, b, c = 1, 2, 3
    while True:
        half = (1 << (n-1)) - 1
        if k <= half: n -= 1; b, c = c, b
        elif k == half + 1: return "%d %d" % (a, c)
        else: k -= half + 1; n -= 1; a, b = b, a

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
