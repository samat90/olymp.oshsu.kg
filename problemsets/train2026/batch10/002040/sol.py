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
    R = [v[1+4*i:5+4*i] for i in range(n)]
    xs = sorted({x for r_ in R for x in (r_[0], r_[2])}); ys = sorted({y for r_ in R for y in (r_[1], r_[3])})
    xi = {x: i for i, x in enumerate(xs)}; yi = {y: i for i, y in enumerate(ys)}
    W, H = len(xs), len(ys)
    D = [[0]*(H+1) for _ in range(W+1)]
    for x1, y1, x2, y2 in R:
        a, b, c, d = xi[x1], yi[y1], xi[x2], yi[y2]
        D[a][b] += 1; D[c][b] -= 1; D[a][d] -= 1; D[c][d] += 1
    tot = 0
    col = [0]*(H+1)
    for i in range(W-1):
        run = 0
        for j in range(H-1):
            col[j] += D[i][j]
            run += col[j]
            if run > 0: tot += (xs[i+1]-xs[i]) * (ys[j+1]-ys[j])
    return tot

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
