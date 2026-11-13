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
    v = list(map(int, s.split())); n = v[0]; h = v[1:]
    return sum(max(0, min(max(h[:i+1]), max(h[i:])) - h[i]) for i in range(n))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
