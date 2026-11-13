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
    n, l, r = map(int, s.split())
    on = [False]*(n+1)
    for i in range(1, n+1):
        for j in range(i, n+1, i): on[j] = not on[j]
    return sum(on[l:r+1])

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
