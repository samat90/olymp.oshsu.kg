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
    n, k = map(int, s.split())
    L = list(range(1, n+1)); i = 0
    while len(L) > 1:
        i = (i + k - 1) % len(L); L.pop(i)
    return L[0]

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
