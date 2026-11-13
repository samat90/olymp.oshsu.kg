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
    m, T_ = map(int, s.split())
    sys.setrecursionlimit(10000)
    @lru_cache(None)
    def f(mask, tot):
        for i in range(m):
            if not mask >> i & 1:
                if tot + i + 1 >= T_ or not f(mask | 1 << i, tot + i + 1): return True
        return False
    return "Айбек" if f(0, 0) else "Бермет"

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
