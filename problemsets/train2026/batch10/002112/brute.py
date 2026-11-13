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
    v = list(map(int, s.split())); n, S = v[0], v[1]; a = v[2:2+n]
    return sum(1 for m in range(1 << n) if sum(a[i] for i in range(n) if m >> i & 1) == S)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
