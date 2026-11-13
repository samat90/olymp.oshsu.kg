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
    k = int(s); black = set(); x = y = 0; dx, dy = 0, 1
    for _ in range(k):
        if (x, y) in black:
            black.discard((x, y)); dx, dy = -dy, dx
        else:
            black.add((x, y)); dx, dy = dy, -dx
        x += dx; y += dy
    return len(black)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
