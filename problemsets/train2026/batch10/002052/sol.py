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
    v = list(map(int, s.split())); k = v[0]; a = v[1:1+k]
    M = max(a); g = [0]*(M+1)
    for n in range(3, M+1):
        seen = set()
        for x in range(1, (n-1)//2 + 1):
            seen.add(g[x] ^ g[n-x])
        m = 0
        while m in seen: m += 1
        g[n] = m
    x = 0
    for q in a: x ^= g[q]
    return "Айбек" if x else "Бермет"

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
