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
    k = int(s); S = 2*k + 5
    g = [[0]*S for _ in range(S)]; x = y = S // 2; d = 0
    D = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    for _ in range(k):
        if g[x][y]: g[x][y] = 0; d = (d - 1) % 4
        else: g[x][y] = 1; d = (d + 1) % 4
        x += D[d][0]; y += D[d][1]
    return sum(map(sum, g))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
