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
    d = {0: 1}
    for x in a:
        nd = defaultdict(int)
        for k, c in d.items(): nd[k+x] += c; nd[k-x] += c
        d = nd
    return d.get(T_, 0)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
