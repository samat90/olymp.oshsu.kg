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
    v = list(map(int, s.split())); n = v[0]; h = v[1:]
    i, j = 0, n-1; best = 0
    while i < j:
        best = max(best, (j-i) * min(h[i], h[j]))
        if h[i] < h[j]: i += 1
        else: j -= 1
    return best

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
