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
    return isqrt(r) - isqrt(l-1)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
