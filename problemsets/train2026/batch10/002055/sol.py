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
    d = a[:]  # d[i] = best diff for segment [i, i+len)
    for ln in range(2, n+1):
        for i in range(n-ln+1):
            d[i] = max(a[i] - d[i+1], a[i+ln-1] - d[i])
    return d[0]

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
