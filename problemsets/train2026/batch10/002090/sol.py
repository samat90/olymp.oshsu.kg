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
    n, k = map(int, s.split()); k -= 1; avail = list(range(1, n+1)); res = []
    for i in range(n, 0, -1):
        f = factorial(i-1); idx = k // f; k %= f
        res.append(avail.pop(idx))
    return " ".join(map(str, res))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
