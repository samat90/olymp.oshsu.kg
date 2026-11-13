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
    v = list(map(int, s.split())); n = v[0]; h = v[1:]
    l, rr = 0, n-1; lm = rm = 0; tot = 0
    while l < rr:
        if h[l] < h[rr]:
            lm = max(lm, h[l]); tot += lm - h[l]; l += 1
        else:
            rm = max(rm, h[rr]); tot += rm - h[rr]; rr -= 1
    return tot

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
