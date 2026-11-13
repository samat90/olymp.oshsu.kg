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
    v = list(map(int, s.split())); d, Nn = v[0], v[1]; a = v[2:2+d]; c = v[2+d:2+2*d]; P = 10**9 + 7
    a = a[:]
    while len(a) <= Nn:
        a.append(sum(c[j]*a[-1-j] for j in range(d)) % P)
    return a[Nn] % P

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
