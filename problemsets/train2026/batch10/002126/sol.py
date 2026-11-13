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
    v = list(map(int, s.split())); a = v[1:1+v[0]]; tot = sum(a); bits = 1
    for x in a: bits |= bits << x
    best = tot
    for k in range(tot // 2, -1, -1):
        if bits >> k & 1: best = tot - 2*k; break
    return best

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
