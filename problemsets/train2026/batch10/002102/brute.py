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
    par = list(range(n*m))
    def f(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for i in range(n):
        for j in range(m):
            if g[i][j] == '1':
                if i+1 < n and g[i+1][j] == '1': par[f(i*m+j)] = f((i+1)*m+j)
                if j+1 < m and g[i][j+1] == '1': par[f(i*m+j)] = f(i*m+j+1)
    return len({f(i*m+j) for i in range(n) for j in range(m) if g[i][j] == '1'})

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
