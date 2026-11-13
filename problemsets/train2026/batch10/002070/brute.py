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
    v = s.split(); n, m = int(v[0]), int(v[1]); g = [list(x) for x in v[2:2+n]]
    ch = True
    while ch:
        ch = False
        for i in range(n-1):
            for j in range(m):
                if g[i][j] == '*' and g[i+1][j] == '.':
                    g[i][j], g[i+1][j] = '.', '*'; ch = True
    return "\n".join("".join(row) for row in g)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
