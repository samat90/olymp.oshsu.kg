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
    v = list(map(int, s.split())); q = v[0]
    @lru_cache(None)
    def w(a, b):
        for da, db in ((1,2),(2,1),(1,1)):
            if a-da >= 0 and b-db >= 0 and not w(a-da, b-db): return True
        return False
    return "\n".join("Айбек" if w(v[1+2*i], v[2+2*i]) else "Бермет" for i in range(q))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
