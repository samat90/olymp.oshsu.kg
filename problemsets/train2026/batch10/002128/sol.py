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
    def find(w):
        used = [[False]*m for _ in range(n)]
        def go(i, j, k):
            if g[i][j] != w[k]: return False
            if k == len(w) - 1: return True
            used[i][j] = True
            for a, b in ((i+1, j), (i-1, j), (i, j+1), (i, j-1)):
                if 0 <= a < n and 0 <= b < m and not used[a][b] and go(a, b, k+1):
                    used[i][j] = False; return True
            used[i][j] = False
            return False
        return any(go(i, j, 0) for i in range(n) for j in range(m))
    return "\n".join("YES" if find(w) else "NO" for w in words)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
