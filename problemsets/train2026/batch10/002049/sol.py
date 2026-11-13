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
    v = list(map(int, s.split())); x = 0
    for a in v[1:]: x ^= a
    return "Айбек" if x else "Бермет"

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
