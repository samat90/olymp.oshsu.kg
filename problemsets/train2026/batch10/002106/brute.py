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
    v = s.split(); T_ = int(v[0]); o = []
    for k in range(T_):
        g = v[1+9*k:10+9*k]; cells = [(i, j) for i in range(9) for j in range(9) if g[i][j] != '0']
        bad = any(g[a][b] == g[c][d] and (a == c or b == d or (a//3, b//3) == (c//3, d//3)) for (a, b), (c, d) in combinations(cells, 2))
        o.append("NO" if bad else "YES")
    return "\n".join(o)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
