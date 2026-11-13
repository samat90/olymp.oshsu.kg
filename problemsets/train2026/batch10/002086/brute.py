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
    d, k = s.split(); k = int(k); n = len(d)
    best = min(int("".join(d[i] for i in c) or "0") for c in combinations(range(n), n-k))
    return str(best)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
