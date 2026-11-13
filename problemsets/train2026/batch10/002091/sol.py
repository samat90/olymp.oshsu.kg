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
    g = s.strip(); res = []; c = 0
    for ch in g:
        c ^= int(ch); res.append(str(c))
    return "".join(res)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
