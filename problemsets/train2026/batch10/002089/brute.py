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
    n, k = map(int, s.split())
    L = []
    for bits in product("()", repeat=2*n):
        b = 0; ok = True
        for c in bits:
            b += 1 if c == '(' else -1
            if b < 0: ok = False; break
        if ok and b == 0: L.append("".join(bits))
    L.sort()
    return L[k-1]

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
