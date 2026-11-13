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
    v = list(map(int, s.split())); n, m = v[0], v[1]; p = 2; INF = float("inf")
    dp = [INF]*m
    for i in range(n):
        for j in range(m):
            x = v[p]; p += 1
            if i == 0 and j == 0: dp[0] = x
            else: dp[j] = min(dp[j], dp[j-1] if j else INF) + x
    return dp[m-1]

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
