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

def N(r, t, tiny, big):
    if t == 0: return r.randint(1, tiny)
    if t == 10: return big
    if t <= 3: return r.randint(1, tiny * 2)
    return max(1, big * t * t // 100)

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

def gen(r, t):
    dg = list(range(1, 10)); r.shuffle(dg)
    R = [3*b + x for b in r.sample([0,1,2], 3) for x in r.sample([0,1,2], 3)]
    C = [3*b + x for b in r.sample([0,1,2], 3) for x in r.sample([0,1,2], 3)]
    g = [[dg[(3*(i % 3) + i // 3 + j) % 9] for j in C] for i in R]
    target = r.randint(42, 50) if t <= 3 else r.randint(26, 32)
    cells = [(i, j) for i in range(9) for j in range(9)]; r.shuffle(cells)
    clues = 81
    for (i, j) in cells:
        if clues <= target: break
        old = g[i][j]; g[i][j] = 0
        if len(solve_sudoku([row[:] for row in g], 2)) != 1: g[i][j] = old
        else: clues -= 1
    return "\n".join("".join(map(str, row)) for row in g) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2116 * 1000 + t)
    sys.stdout.write(gen(r, t))
