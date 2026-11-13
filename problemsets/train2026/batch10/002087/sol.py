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
    a, b = s.split(); a += '{'; b += '{'; i = j = 0; res = []
    n, m = len(a)-1, len(b)-1
    while i < n or j < m:
        if a[i:] <= b[j:]: res.append(a[i]); i += 1
        else: res.append(b[j]); j += 1
    return "".join(res)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
