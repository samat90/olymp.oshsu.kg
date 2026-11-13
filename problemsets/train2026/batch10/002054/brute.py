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
    v = list(map(int, s.split())); a = v[1:1+v[0]]
    o = []
    for n in a:
        @lru_cache(None)
        def w(mask):
            for i in range(n):
                if not (mask >> i) & 1:
                    if not w(mask | 1 << i): return True
                    if i+1 < n and not (mask >> (i+1)) & 1 and not w(mask | 1 << i | 1 << (i+1)): return True
            return False
        o.append("Айбек" if w(0) else "Бермет")
    return "\n".join(o)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
