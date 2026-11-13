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
    for j in range(m):
        free = n - 1
        for i in range(n-1, -1, -1):
            if g[i][j] == 'X': free = i - 1
            elif g[i][j] == '*':
                g[i][j] = '.'; g[free][j] = '*'; free -= 1
    return "\n".join("".join(row) for row in g)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
