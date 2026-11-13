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
    s = s.strip(); L = []; R = []
    for c in s:
        if c == '<':
            if L: R.append(L.pop())
        elif c == '>':
            if R: L.append(R.pop())
        elif c == '-':
            if L: L.pop()
        else: L.append(c)
    return "".join(L) + "".join(reversed(R))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
