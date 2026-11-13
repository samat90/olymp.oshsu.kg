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
    M = max(a); win = [False]*(M+1)
    for x in range(1, M+1):
        for ch in set(str(x)):
            d = int(ch)
            if d and not win[x-d]: win[x] = True; break
    return "\n".join("Айбек" if win[q] else "Бермет" for q in a)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
