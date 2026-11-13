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
    v = list(map(int, s.split())); t = v[0]
    M = max(max(v[1::2]), max(v[2::2])) + 1
    P = set(); used = [False]*(2*M+10); k = 0; a = 0
    lose = set()
    while True:
        while a < len(used) and used[a]: a += 1
        if a > M: break
        b = a + k
        lose.add((a, b)); lose.add((b, a))
        used[a] = True
        if b < len(used): used[b] = True
        k += 1
    o = []
    for i in range(t):
        x, y = v[1+2*i], v[2+2*i]
        o.append("Бермет" if (x, y) in lose else "Айбек")
    return "\n".join(o)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
