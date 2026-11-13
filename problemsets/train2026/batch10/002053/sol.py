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
    v = list(map(int, s.split())); a = v[1:]
    x = 0
    for q in a: x ^= q
    if max(a) <= 1:
        return "Айбек" if sum(a) % 2 == 0 else "Бермет"
    return "Айбек" if x else "Бермет"

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
