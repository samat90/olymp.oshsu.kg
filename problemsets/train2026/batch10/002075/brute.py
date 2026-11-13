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
    v = s.split(); n, q = int(v[0]), int(v[1]); i = 2
    a = list(range(1, n+1))
    for _ in range(q):
        if v[i] == '1':
            x = int(v[i+1]) % n; i += 2
            a = a[-x:] + a[:-x] if x else a
        else:
            i += 1
            for j in range(0, n, 2): a[j], a[j+1] = a[j+1], a[j]
    return " ".join(map(str, a))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
