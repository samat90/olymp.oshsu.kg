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
    v = list(map(int, s.split())); n = v[0]; h = v[1:]
    return max((j-i)*min(h[i], h[j]) for i in range(n) for j in range(i+1, n))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
