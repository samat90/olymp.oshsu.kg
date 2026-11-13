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
    n = int(s); k = 1
    while True:
        v = int(bin(k)[2:])
        if v % n == 0: return str(v)
        k += 1

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
