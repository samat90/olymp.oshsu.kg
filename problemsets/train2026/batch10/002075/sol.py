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
    p0, p1 = 0, 1   # позиции (с 0) ребёнка 1 и ребёнка 2
    for _ in range(q):
        if v[i] == '1':
            x = int(v[i+1]); i += 2; p0 = (p0 + x) % n; p1 = (p1 + x) % n
        else:
            i += 1
            p0 += 1 if p0 % 2 == 0 else -1; p1 += 1 if p1 % 2 == 0 else -1
    res = [0]*n
    for c in range(0, n, 2):
        res[(p0 + c) % n] = c + 1; res[(p1 + c) % n] = c + 2
    return " ".join(map(str, res))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
