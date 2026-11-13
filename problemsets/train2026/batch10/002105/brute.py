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
    v = s.split(); n, m = int(v[0]), int(v[1]); cnt = 0
    eq = [([int(c) for c in v[2+2*i]], int(v[3+2*i])) for i in range(n)]
    for xs in product((0, 1), repeat=m):
        if all(sum(a*b for a, b in zip(row, xs)) % 2 == rhs for row, rhs in eq): cnt += 1
    return cnt % (10**9 + 7)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
