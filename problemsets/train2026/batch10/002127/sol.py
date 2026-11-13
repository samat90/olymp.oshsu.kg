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
    v = s.split(); n, m = int(v[0]), int(v[1]); g = v[2:2+n]; free = 0; st = en = None
    for i in range(n):
        for j in range(m):
            if g[i][j] != '#': free += 1
            if g[i][j] == 'S': st = (i, j)
            if g[i][j] == 'E': en = (i, j)
    seen = [[False]*m for _ in range(n)]
    def go(i, j, left):
        if (i, j) == en: return 1 if left == 0 else 0
        seen[i][j] = True; c = 0
        for a, b in ((i+1, j), (i-1, j), (i, j+1), (i, j-1)):
            if 0 <= a < n and 0 <= b < m and g[a][b] != '#' and not seen[a][b]: c += go(a, b, left-1)
        seen[i][j] = False
        return c
    return go(st[0], st[1], free - 1)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
