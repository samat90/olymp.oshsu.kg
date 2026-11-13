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
    v = list(map(int, s.split())); n, m = v[0], v[1]; a = [v[2+i*m:2+(i+1)*m] for i in range(n)]
    t, b, l, r_ = 0, n-1, 0, m-1; o = []
    while t <= b and l <= r_:
        o += a[t][l:r_+1]
        o += [a[i][r_] for i in range(t+1, b+1)]
        if t < b: o += a[b][l:r_][::-1]
        if l < r_: o += [a[i][l] for i in range(b-1, t, -1)]
        t += 1; b -= 1; l += 1; r_ -= 1
    return " ".join(map(str, o))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
