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
    n = int(s); P = 10**9 + 7; f = [1, 1, 2, 5] + [0]*max(0, n-2)
    for i in range(4, n+1): f[i] = (2*f[i-1] + f[i-3]) % P
    return f[n] % P

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
