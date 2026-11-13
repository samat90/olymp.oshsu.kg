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
    v = list(map(int, s.split())); a = v[1:1+v[0]]; M = max(a)
    g = [0]*(M+1)
    for n in range(2, M+1):
        seen = {g[n-j] for j in range(1, n//2 + 1)}
        m = 0
        while m in seen: m += 1
        g[n] = m
    x = 0
    for q in a: x ^= g[q]
    return "Айбек" if x else "Бермет"

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
