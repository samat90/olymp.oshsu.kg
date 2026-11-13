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
    v = list(map(int, s.split())); n, T_ = v[0], v[1]; a = v[2:2+n]
    return sum(1 for sg in product((1, -1), repeat=n) if sum(x*y for x, y in zip(a, sg)) == T_)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
