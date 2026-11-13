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
    n = int(s); dp = [1] + [0]*n
    for k in range(1, n+1):
        for x in range(k, n+1): dp[x] += dp[x-k]
    return dp[n]

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
