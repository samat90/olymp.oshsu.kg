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
    v = list(map(int, s.split())); n, m = v[0], v[1]; E = [(v[2+2*i]-1, v[3+2*i]-1) for i in range(m)]
    for k in range(1, n+1):
        for col in product(range(k), repeat=n):
            if all(col[a] != col[b] for a, b in E): return k

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
