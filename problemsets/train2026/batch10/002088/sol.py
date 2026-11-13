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
    v = list(map(int, s.split())); n, k = v[0], v[1]; a = v[2:2+n]
    for i in range(n):
        if k == 0: break
        hi = min(n-1, i+k)
        j = min(range(i, hi+1), key=lambda x: a[x])
        x = a.pop(j); a.insert(i, x); k -= j - i
    return " ".join(map(str, a))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
