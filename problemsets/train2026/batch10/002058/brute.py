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
    M = 22
    win = [[False]*(M+1) for _ in range(M+1)]
    for x in range(M+1):
        for y in range(M+1):
            if (x, y) == (0, 0): continue
            moves = [(a, y) for a in range(x)] + [(x, b) for b in range(y)] + [(x-d, y-d) for d in range(1, min(x, y)+1)]
            win[x][y] = any((a, b) == (0, 0) or not win[a][b] for a, b in moves)
    return "\n".join("Айбек" if win[v[1+2*i]][v[2+2*i]] else "Бермет" for i in range(t))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
