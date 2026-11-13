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
    v = list(map(int, s.split())); q = v[0]
    M = max(v[1:]) + 1
    win = [[False]*M for _ in range(M)]
    for a in range(M):
        for b in range(M):
            w = False
            if a >= 1 and b >= 2 and not win[a-1][b-2]: w = True
            elif a >= 2 and b >= 1 and not win[a-2][b-1]: w = True
            elif a >= 1 and b >= 1 and not win[a-1][b-1]: w = True
            win[a][b] = w
    return "\n".join("Айбек" if win[v[1+2*i]][v[2+2*i]] else "Бермет" for i in range(q))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
