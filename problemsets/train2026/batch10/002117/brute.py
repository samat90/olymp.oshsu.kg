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
    k, n = map(int, s.split())
    L = [c for c in combinations(range(1, 10), k) if sum(c) == n]
    return "\n".join([str(len(L))] + [" ".join(map(str, c)) for c in L])

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
