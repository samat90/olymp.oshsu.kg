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
    n, m = map(int, s.split())
    res = [0]*n; i = 0; give = 1
    while m > 0:
        g = min(give, m); res[i] += g; m -= g; give += 1; i = (i+1) % n
    return " ".join(map(str, res))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
