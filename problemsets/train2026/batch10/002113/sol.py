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
    n, d = map(int, s.split()); P = 10**9 + 7
    dp = [0]*(d+2); dp[0] = 1
    for _ in range(2*n):
        nd = [0]*(d+2)
        for b in range(d+1):
            if dp[b]:
                if b < d: nd[b+1] = (nd[b+1] + dp[b]) % P
                if b > 0: nd[b-1] = (nd[b-1] + dp[b]) % P
        dp = nd
    return dp[0]

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
