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
    v = s.split(); n, m = int(v[0]), int(v[1]); a = [list(map(int, v[2+i*m:2+(i+1)*m])) for i in range(n)]; ops = v[2+n*m]
    for c in ops:
        if c == 'R': a = [list(x)[::-1] for x in zip(*a)]
        elif c == 'H': a = [x[::-1] for x in a]
        elif c == 'V': a = a[::-1]
        else: a = [list(x) for x in zip(*a)]
    return mat_text(a)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
