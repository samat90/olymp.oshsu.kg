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
    v = list(map(int, s.split())); n = v[0]; a = v[1:]
    seen = set()
    def go(i, st, nxt):
        if nxt == n+1: return True
        key = (i, st, nxt)
        if key in seen: return False
        seen.add(key)
        if st and st[-1] == nxt and go(i, st[:-1], nxt+1): return True
        if i < n and go(i+1, st + (a[i],), nxt): return True
        return False
    return "YES" if go(0, (), 1) else "NO"

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
