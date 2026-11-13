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
    s = s.strip(); t = ""; p = 0
    for c in s:
        if c == '[': p = 0
        elif c == ']': p = len(t)
        else: t = t[:p] + c + t[p:]; p += 1
    return t

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
