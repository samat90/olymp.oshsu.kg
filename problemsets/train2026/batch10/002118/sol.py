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
    dp = [[0]*n for _ in range(1 << n)]
    for i in range(n): dp[1 << i][i] = 1
    for mask in range(1, 1 << n):
        row = dp[mask]
        for last in range(n):
            c = row[last]
            if c:
                nb = adj[last] & ~mask
                while nb:
                    b = nb & -nb; nb ^= b
                    dp[mask | b][b.bit_length()-1] += c
    return sum(dp[(1 << n) - 1])

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
