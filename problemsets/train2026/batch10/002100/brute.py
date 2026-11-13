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
    for k in range(1, min(n, m)+1):
        for i in range(n-k+1):
            for j in range(m-k+1):
                if all(g[x][y] == '1' for x in range(i, i+k) for y in range(j, j+k)): best = k
    return best

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
