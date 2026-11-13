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
    n, d = map(int, s.split()); cnt = 0
    for bits in product((1, -1), repeat=2*n):
        b = 0; ok = True
        for x in bits:
            b += x
            if b < 0 or b > d: ok = False; break
        if ok and b == 0: cnt += 1
    return cnt % (10**9 + 7)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
