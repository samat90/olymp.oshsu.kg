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
    n = int(s); L = 1 << n
    sys.setrecursionlimit(10000)
    def dfs(cur, used):
        m = len(cur)
        if m == L:
            ext = cur + cur[:n-1]
            return cur if len({ext[i:i+n] for i in range(L)}) == L else None
        for c in "01":
            nc = cur + c
            if len(nc) >= n:
                w = nc[-n:]
                if w in used: continue
                nu = used | {w}
            else: nu = used
            r_ = dfs(nc, nu)
            if r_: return r_
        return None
    return dfs("", frozenset())

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
