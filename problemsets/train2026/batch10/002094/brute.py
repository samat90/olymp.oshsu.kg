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
    seen = [[False]*m for _ in range(n)]; i = j = d = 0; o = []
    D = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    for _ in range(n*m):
        o.append(a[i][j]); seen[i][j] = True
        ni, nj = i + D[d][0], j + D[d][1]
        if not (0 <= ni < n and 0 <= nj < m and not seen[ni][nj]):
            d = (d+1) % 4; ni, nj = i + D[d][0], j + D[d][1]
        i, j = ni, nj
    return " ".join(map(str, o))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
