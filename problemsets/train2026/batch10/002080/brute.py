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
    v = s.split("\n"); S = v[0].strip(); k = int(v[1])
    ch = True
    while ch:
        ch = False
        for i in range(len(S) - k + 1):
            if S[i:i+k] == S[i] * k:
                S = S[:i] + S[i+k:]; ch = True; break
    return S

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
