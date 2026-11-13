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
    def go(i):
        if i == n: return -1
        return min(1 + go(j) for j in range(i+1, n+1) if s[i:j] == s[i:j][::-1])
    return go(0)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
