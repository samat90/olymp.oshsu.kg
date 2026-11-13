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
    v = list(map(int, s.split())); n, m = v[0], v[1]; adj = [0]*n
    for i in range(m):
        a, b = v[2+2*i]-1, v[3+2*i]-1; adj[a] |= 1 << b; adj[b] |= 1 << a
    full = (1 << n) - 1
    ind = [True]*(1 << n)
    for mask in range(1, 1 << n):
        low = (mask & -mask).bit_length() - 1; rest = mask & (mask - 1)
        ind[mask] = ind[rest] and not (adj[low] & rest)
    INF = 99; dp = [INF]*(1 << n); dp[0] = 0
    for mask in range(1, 1 << n):
        low = mask & -mask; sub = mask
        while sub:
            if sub & low and ind[sub]:
                if dp[mask ^ sub] + 1 < dp[mask]: dp[mask] = dp[mask ^ sub] + 1
            sub = (sub - 1) & mask
    return dp[full]

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
