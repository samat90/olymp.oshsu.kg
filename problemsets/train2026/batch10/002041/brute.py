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
    return sum(1 for x in range(-R, R+1) for y in range(-R, R+1) if x*x+y*y <= R*R)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
