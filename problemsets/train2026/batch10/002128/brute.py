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
    v = s.split(); n, m = int(v[0]), int(v[1]); g = v[2:2+n]; q = int(v[2+n]); words = v[3+n:3+n+q]
    strs = set()
    def ext(path, txt):
        strs.add(txt)
        if len(txt) >= 10: return
        i, j = path[-1]
        for a, b in ((i+1, j), (i-1, j), (i, j+1), (i, j-1)):
            if 0 <= a < n and 0 <= b < m and (a, b) not in path: ext(path + [(a, b)], txt + g[a][b])
    for i in range(n):
        for j in range(m): ext([(i, j)], g[i][j])
    return "\n".join("YES" if w in strs else "NO" for w in words)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
