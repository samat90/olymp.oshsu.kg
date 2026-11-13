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
    v = list(map(int, s.split())); n, m = v[0], v[1]; a = v[2:2+m]
    win = [False]*(n+1)
    for x in range(1, n+1):
        for d in a:
            if d <= x and not win[x-d]: win[x] = True; break
    return "Айбек" if win[n] else "Бермет"

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
