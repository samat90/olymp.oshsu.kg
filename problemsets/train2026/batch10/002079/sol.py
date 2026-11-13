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
    n, m = map(int, s.split())
    k = (isqrt(8*m + 1) - 1) // 2
    while k*(k+1)//2 > m: k -= 1
    while (k+1)*(k+2)//2 <= m: k += 1
    rem = m - k*(k+1)//2
    res = []
    for i in range(n):
        first = i + 1
        if first > k: c = 0
        else: c = (k - first) // n + 1
        res.append(c*first + n*c*(c-1)//2)
    res[k % n] += rem
    return " ".join(map(str, res))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
