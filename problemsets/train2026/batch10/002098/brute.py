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
    p = 2 + n*m; q = v[p]; p += 1; o = []
    for _ in range(q):
        r1, c1, r2, c2 = v[p:p+4]; p += 4
        o.append(sum(a[i][j] for i in range(r1-1, r2) for j in range(c1-1, c2)))
    return "\n".join(map(str, o))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
