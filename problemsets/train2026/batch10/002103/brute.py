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
    i = j = 0; up = True; o = []
    for _ in range(n*m):
        o.append(a[i][j])
        if up:
            if j == m-1: i += 1; up = False
            elif i == 0: j += 1; up = False
            else: i -= 1; j += 1
        else:
            if i == n-1: j += 1; up = True
            elif j == 0: i += 1; up = True
            else: i += 1; j -= 1
    return " ".join(map(str, o))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
