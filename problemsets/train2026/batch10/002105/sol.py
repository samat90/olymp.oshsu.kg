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
    v = s.split(); n, m = int(v[0]), int(v[1]); rows = []
    for i in range(n):
        rows.append(int(v[2+2*i], 2) << 1 | int(v[3+2*i]))
    rank = 0
    for col in range(m, 0, -1):    # бит col соответствует переменной; свободный член — бит 0
        piv = None
        for i in range(rank, n):
            if rows[i] >> col & 1: piv = i; break
        if piv is None: continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for i in range(n):
            if i != rank and rows[i] >> col & 1: rows[i] ^= rows[rank]
        rank += 1
    for i in range(rank, n):
        if rows[i] == 1: return 0
    return pow(2, m - rank, 10**9 + 7)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
