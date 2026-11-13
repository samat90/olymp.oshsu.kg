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

def solve_sudoku(g, limit=2):
    rows = [0]*9; cols = [0]*9; blks = [0]*9
    cells = []
    for i in range(9):
        for j in range(9):
            if g[i][j]:
                b = 1 << g[i][j]; rows[i] |= b; cols[j] |= b; blks[i//3*3+j//3] |= b
            else: cells.append((i, j))
    sols = []
    def go():
        if len(sols) >= limit: return
        best = None; bm = None; bc = 10
        for (i, j) in cells:
            if g[i][j]: continue
            m = ~(rows[i] | cols[j] | blks[i//3*3+j//3]) & 0x3FE
            c = bin(m).count("1")
            if c < bc: bc = c; best = (i, j); bm = m
            if c == 0: return
        if best is None:
            sols.append([row[:] for row in g]); return
        i, j = best
        while bm:
            b = bm & -bm; bm ^= b; d = b.bit_length() - 1
            g[i][j] = d; rows[i] |= b; cols[j] |= b; blks[i//3*3+j//3] |= b
            go()
            g[i][j] = 0; rows[i] ^= b; cols[j] ^= b; blks[i//3*3+j//3] ^= b
    go()
    return sols

def solve(s):
    g = [[int(c) for c in row] for row in s.split()]
    def ok(i, j, d):
        for k in range(9):
            if g[i][k] == d or g[k][j] == d: return False
        bi, bj = i//3*3, j//3*3
        return all(g[bi+x][bj+y] != d for x in range(3) for y in range(3))
    def go(p):
        while p < 81 and g[p//9][p%9]: p += 1
        if p == 81: return True
        i, j = divmod(p, 9)
        for d in range(1, 10):
            if ok(i, j, d):
                g[i][j] = d
                if go(p+1): return True
                g[i][j] = 0
        return False
    go(0)
    return "\n".join("".join(map(str, row)) for row in g)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
