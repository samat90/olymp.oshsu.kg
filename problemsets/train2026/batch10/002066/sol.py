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
    s = s.strip(); x = y = 0; seen = {(0, 0)}
    for c in s:
        if c == 'U': y += 1
        elif c == 'D': y -= 1
        elif c == 'L': x -= 1
        else: x += 1
        seen.add((x, y))
    return len(seen)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
