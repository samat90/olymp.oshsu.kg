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
    v = list(map(int, s.split())); n = v[0]; a = v[1:1+n]; tot = sum(a)
    return min(abs(tot - 2*sum(a[i] for i in range(n) if m >> i & 1)) for m in range(1 << n))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
