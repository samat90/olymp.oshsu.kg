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
    v = s.split(); n, m = int(v[0]), int(v[1]); a = [list(map(int, v[2+i*m:2+(i+1)*m])) for i in range(n)]; ops = v[2+n*m]
    tr = fr = fc = 0   # итог = (транспонирование tr) затем реверс строк fr и столбцов fc
    def do(c):
        nonlocal tr, fr, fc
        if c == 'H': fc ^= 1
        elif c == 'V': fr ^= 1
        else: tr ^= 1; fr, fc = fc, fr
    for c in ops:
        if c == 'R': do('T'); do('H')
        else: do(c)
    if tr: a = [list(x) for x in zip(*a)]
    if fr: a = a[::-1]
    if fc: a = [x[::-1] for x in a]
    return mat_text(a)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
