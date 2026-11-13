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
    v = s.split(); n, m = int(v[0]), int(v[1]); g = v[2:2+n]; best = 0
    for i in range(n):
        for j in range(m):
            for i2 in range(i, n):
                for j2 in range(j, m):
                    if all(g[x][y] == '1' for x in range(i, i2+1) for y in range(j, j2+1)):
                        best = max(best, (i2-i+1)*(j2-j+1))
    return best

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
