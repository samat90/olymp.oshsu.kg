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
    v = list(map(int, s.split())); n = v[0]
    cells = set()
    for i in range(n):
        x1,y1,x2,y2 = v[1+4*i:5+4*i]
        for x in range(x1, x2):
            for y in range(y1, y2): cells.add((x, y))
    return len(cells)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
