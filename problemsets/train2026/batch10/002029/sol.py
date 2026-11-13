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
    a = list(map(int, s.split()))
    return abs((a[2]-a[0])*(a[5]-a[1]) - (a[3]-a[1])*(a[4]-a[0]))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
