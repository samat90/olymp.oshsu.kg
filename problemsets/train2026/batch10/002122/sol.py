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
    s = s.strip(); n = len(s)
    # простая DP по подстрокам
    pal = [[False]*n for _ in range(n)]
    for i in range(n-1, -1, -1):
        for j in range(i, n):
            pal[i][j] = s[i] == s[j] and (j - i < 2 or pal[i+1][j-1])
    dp = [0]*n
    for j in range(n):
        if pal[0][j]: dp[j] = 0
        else: dp[j] = min(dp[i-1] + 1 for i in range(1, j+1) if pal[i][j])
    return dp[n-1]

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
