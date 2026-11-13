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
    v = list(map(int, s.split())); o = []
    for i in range(v[0]):
        n, k = v[1+2*i], v[2+2*i]
        o.append("Айбек" if n % (k+1) else "Бермет")
    return "\n".join(o)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
