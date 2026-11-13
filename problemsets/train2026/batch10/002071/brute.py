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
        if c == '<': p = max(0, p-1)
        elif c == '>': p = min(len(t), p+1)
        elif c == '-':
            if p > 0: t = t[:p-1] + t[p:]; p -= 1
        else: t = t[:p] + c + t[p:]; p += 1
    return t

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
