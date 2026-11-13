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
    def f(rest, tot):
        for x in rest:
            if tot + x >= T_ or not f(rest - {x}, tot + x): return True
        return False
    return "Айбек" if f(frozenset(range(1, m+1)), 0) else "Бермет"

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
