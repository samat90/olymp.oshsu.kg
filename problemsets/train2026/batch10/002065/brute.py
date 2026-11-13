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
    L = list(range(1, n+1)); i = 0; o = []
    while L:
        i = (i + k - 1) % len(L); o.append(L.pop(i))
        if L: i %= len(L)
    return " ".join(map(str, o))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
