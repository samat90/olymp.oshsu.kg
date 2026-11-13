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
    v = list(map(int, s.split())); n = v[0]; a = v[1:1+n]; seen = {}; step = 0
    while tuple(a) not in seen:
        seen[tuple(a)] = step
        i = a.index(max(a)); c = a[i]; a[i] = 0
        for j in range(1, c+1): a[(i+j) % n] += 1
        step += 1
    return "%d %d" % (step, step - seen[tuple(a)])

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
