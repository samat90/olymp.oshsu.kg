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
    v = list(map(int, s.split())); n = v[0]
    H = [0]*40; out = []
    for i in range(n):
        l, w = v[1+2*i], v[2+2*i]
        top = max(H[l:l+w]) + 1
        for x in range(l, l+w): H[x] = top
        out.append(max(H))
    return " ".join(map(str, out))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
