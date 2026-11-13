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
    w, h, x, y, dx, dy, t = map(int, s.split())
    for _ in range(t):
        if not 0 <= x + dx <= w: dx = -dx
        if not 0 <= y + dy <= h: dy = -dy
        x += dx; y += dy
    return "%d %d" % (x, y)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
