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
    w = min(a[2], a[6]) - max(a[0], a[4]); h = min(a[3], a[7]) - max(a[1], a[5])
    return w*h if w > 0 and h > 0 else 0

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
