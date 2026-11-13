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
    n = int(s)
    def go(rest, mx):
        if rest == 0: return 1
        return sum(go(rest-k, k) for k in range(1, min(rest, mx)+1))
    return go(n, n)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
