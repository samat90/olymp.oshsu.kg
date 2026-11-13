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
    v = list(map(int, s.split())); n, m = v[0], v[1]; E = set()
    for i in range(m):
        a, b = v[2+2*i], v[3+2*i]; E.add((a, b)); E.add((b, a))
    return sum(1 for p in permutations(range(1, n+1)) if all((p[i], p[i+1]) in E for i in range(n-1)))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
