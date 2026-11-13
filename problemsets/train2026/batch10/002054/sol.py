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
    v = list(map(int, s.split())); a = v[1:1+v[0]]
    M = max(a); g = [0]*(M+1)
    for n in range(1, M+1):
        seen = set()
        for x in range(0, n):
            seen.add(g[x] ^ g[n-1-x])
        for x in range(0, n-1):
            seen.add(g[x] ^ g[n-2-x])
        m = 0
        while m in seen: m += 1
        g[n] = m
    return "\n".join("Айбек" if g[q] else "Бермет" for q in a)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
