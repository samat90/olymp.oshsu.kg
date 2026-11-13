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
    v = s.split(); T_ = int(v[0]); o = []
    for k in range(T_):
        g = v[1+9*k:10+9*k]; ok = True
        rowset = [set() for _ in range(9)]; colset = [set() for _ in range(9)]; blk = [set() for _ in range(9)]
        for i in range(9):
            for j in range(9):
                c = g[i][j]
                if c == '0': continue
                b = i//3*3 + j//3
                if c in rowset[i] or c in colset[j] or c in blk[b]: ok = False
                rowset[i].add(c); colset[j].add(c); blk[b].add(c)
        o.append("YES" if ok else "NO")
    return "\n".join(o)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
