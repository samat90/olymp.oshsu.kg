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
    def w(st):
        for i in range(len(st)):
            for j in range(1, st[i]//2 + 1):
                ns = tuple(sorted(st[:i] + (st[i]-j,) + st[i+1:]))
                if not w(ns): return True
        return False
    return "Айбек" if w(tuple(sorted(a))) else "Бермет"

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
