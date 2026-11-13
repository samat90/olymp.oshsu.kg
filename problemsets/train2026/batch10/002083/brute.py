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
    v = list(map(int, s.split())); n = v[0]; a = v[1:1+n]; hist = []
    while a not in hist:
        hist.append(a[:])
        m = max(a); i = min(k for k in range(n) if a[k] == m)
        a[i] = 0
        for j in range(1, m+1): a[(i+j) % n] += 1
    return "%d %d" % (len(hist), len(hist) - hist.index(a))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
