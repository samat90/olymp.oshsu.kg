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
    v = list(map(int, s.split())); n, k = v[0], v[1]; a = tuple(v[2:2+n])
    seen = {a}; fr = [a]
    for _ in range(min(k, n*n)):
        nf = []
        for p in fr:
            for i in range(n-1):
                q = list(p); q[i], q[i+1] = q[i+1], q[i]; q = tuple(q)
                if q not in seen: seen.add(q); nf.append(q)
        fr = nf
        if not fr: break
    return " ".join(map(str, min(seen)))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
