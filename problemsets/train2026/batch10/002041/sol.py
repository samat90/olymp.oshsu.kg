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
    R = int(s)
    tot = 0
    for x in range(-R, R+1):
        tot += 2 * isqrt(R*R - x*x) + 1
    return tot

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
