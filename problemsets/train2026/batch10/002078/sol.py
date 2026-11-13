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
    v = s.split(); n = int(v[0]); g = [list(map(int, v[1+i*n:1+(i+1)*n])) for i in range(n)]; d = v[1+n*n]
    def mv(line):
        a = [x for x in line if x]; res = []; i = 0
        while i < len(a):
            if i+1 < len(a) and a[i] == a[i+1]: res.append(2*a[i]); i += 2
            else: res.append(a[i]); i += 1
        return res + [0]*(n - len(res))
    if d == 'L': g = [mv(r_) for r_ in g]
    elif d == 'R': g = [mv(r_[::-1])[::-1] for r_ in g]
    else:
        cols = [[g[i][j] for i in range(n)] for j in range(n)]
        cols = [mv(c) for c in cols] if d == 'U' else [mv(c[::-1])[::-1] for c in cols]
        g = [[cols[j][i] for j in range(n)] for i in range(n)]
    return "\n".join(" ".join(map(str, r_)) for r_ in g)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
