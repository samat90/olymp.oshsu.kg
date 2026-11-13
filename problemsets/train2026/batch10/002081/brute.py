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
    v = list(map(int, s.split())); n, p = v[0], v[1] - 1; a = v[2:2+n]
    q = list(enumerate(a)); printed = 0
    while True:
        i, x = q.pop(0)
        if any(y > x for _, y in q): q.append((i, x))
        else:
            printed += 1
            if i == p: return printed

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
