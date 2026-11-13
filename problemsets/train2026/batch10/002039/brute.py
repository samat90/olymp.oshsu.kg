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
    a = list(map(int, s.split()))
    c = 0
    for x in range(-7, 7):
        for y in range(-7, 7):
            if a[0] <= x < a[2] and a[1] <= y < a[3] and a[4] <= x < a[6] and a[5] <= y < a[7]: c += 1
    return c

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
