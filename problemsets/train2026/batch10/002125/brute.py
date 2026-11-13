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
    n, h = map(int, s.split())
    def shapes(k):
        if k == 0: return [0]
        res = []
        for l in range(k):
            for a in shapes(l):
                for b in shapes(k-1-l): res.append(1 + max(a, b))
        return res
    return sum(1 for x in shapes(n) if x <= h) % (10**9 + 7)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
