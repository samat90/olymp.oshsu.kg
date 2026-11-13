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
    v = s.split(); n, m, k = int(v[0]), int(v[1]), int(v[2]); g = [[c == '#' for c in row] for row in v[3:3+n]]
    for _ in range(k):
        ng = [[False]*m for _ in range(n)]
        for i in range(n):
            for j in range(m):
                c = 0
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        if di or dj: c += g[(i+di) % n][(j+dj) % m]
                ng[i][j] = c == 3 or (g[i][j] and c == 2)
        g = ng
    return "\n".join("".join('#' if c else '.' for c in row) for row in g)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
