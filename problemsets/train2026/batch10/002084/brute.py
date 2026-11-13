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
    v = s.split(); n = int(v[0]); pat = v[1]
    for p in permutations(range(1, n+1)):
        if all((p[i] < p[i+1]) == (pat[i] == 'I') for i in range(n-1)): return " ".join(map(str, p))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
