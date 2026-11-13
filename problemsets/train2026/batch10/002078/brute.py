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
    v = s.split(); n = int(v[0]); g = [list(map(int, v[1+i*n:1+(i+1)*n])) for i in range(n)]; d = v[1+n*n]
    # поворачиваем так, чтобы сдвиг был влево
    k = {'L': 0, 'D': 1, 'R': 2, 'U': 3}[d]
    def rot(m): return [list(r_) for r_ in zip(*m[::-1])]   # по часовой
    def rotb(m): return [list(r_) for r_ in zip(*m)][::-1]  # против часовой
    for _ in range(k): g = rotb(g) if False else rot(g)
    # после k поворотов по часовой нужное направление — влево? проверяем: D -> поворот по часовой делает «вниз» влево
    for row in g:
        changed = True
        # сжатие
        vals = [x for x in row if x]
        out = []; skip = False
        for i, x in enumerate(vals):
            if skip: skip = False; continue
            if i+1 < len(vals) and vals[i+1] == x: out.append(2*x); skip = True
            else: out.append(x)
        row[:] = out + [0]*(n-len(out))
    for _ in range(k): g = rotb(g)
    return "\n".join(" ".join(map(str, r_)) for r_ in g)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
