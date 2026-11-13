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
    v = list(map(int, s.split())); n, S = v[0], v[1]; a = v[2:2+n]
    def sums(b):
        d = {0: 1}
        for x in b:
            nd = dict(d)
            for k, c in d.items(): nd[k+x] = nd.get(k+x, 0) + c
            d = nd
        return d
    h = n // 2; L = sums(a[:h]); R = sums(a[h:])
    return sum(c * R.get(S-k, 0) for k, c in L.items())

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
