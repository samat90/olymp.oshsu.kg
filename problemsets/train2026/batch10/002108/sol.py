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
    v = s.split(); n, m = int(v[0]), int(v[1]); g = v[2:2+n]; P = 10**9 + 7
    dp = [0]*m
    for i in range(n):
        for j in range(m):
            if g[i][j] == '#': dp[j] = 0
            elif i == 0 and j == 0: dp[j] = 1
            else: dp[j] = (dp[j] + (dp[j-1] if j else 0)) % P
    return dp[m-1]

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
