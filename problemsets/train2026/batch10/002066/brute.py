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
    G = [[0]*(2*n+3) for _ in range(2*n+3)]
    x = y = n+1; G[x][y] = 1
    for c in s:
        if c == 'U': y += 1
        elif c == 'D': y -= 1
        elif c == 'L': x -= 1
        else: x += 1
        G[x][y] = 1
    return sum(map(sum, G))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
