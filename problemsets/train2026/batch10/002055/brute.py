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
    v = list(map(int, s.split())); n = v[0]; a = v[1:]
    def f(l, r):
        if l > r: return 0
        return max(a[l] - f(l+1, r), a[r] - f(l, r-1))
    return f(0, n-1)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
