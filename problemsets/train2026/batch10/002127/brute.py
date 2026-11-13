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
    v = s.split(); n, m = int(v[0]), int(v[1]); g = v[2:2+n]
    cells = [(i, j) for i in range(n) for j in range(m) if g[i][j] != '#']
    st = next(c for c in cells if g[c[0]][c[1]] == 'S'); en = next(c for c in cells if g[c[0]][c[1]] == 'E')
    mid = [c for c in cells if c != st and c != en]; cnt = 0
    for p in permutations(mid):
        path = (st,) + p + (en,)
        if all(abs(a[0]-b[0]) + abs(a[1]-b[1]) == 1 for a, b in zip(path, path[1:])): cnt += 1
    return cnt

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
