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
    v = s.split(); n, m = int(v[0]), int(v[1]); g = v[2:2+n]
    prev = [0]*(m+1); best = 0
    for i in range(n):
        cur = [0]*(m+1)
        row = g[i]
        for j in range(m):
            if row[j] == '1':
                x = min(prev[j], prev[j+1], cur[j]) + 1
                cur[j+1] = x
                if x > best: best = x
        prev = cur
    return best

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
