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
    @lru_cache(None)
    def w(n): return any(not w(n-k*k) for k in range(1, isqrt(n)+1))
    return "\n".join("Айбек" if w(q) else "Бермет" for q in a)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
