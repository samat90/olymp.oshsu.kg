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
    n, k = map(int, s.split()); mv = []
    def h(n, a, b, c):
        if n == 0: return
        h(n-1, a, c, b); mv.append((a, c)); h(n-1, b, a, c)
    h(n, 1, 2, 3)
    return "%d %d" % mv[k-1]

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
