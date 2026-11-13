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
    v = s.split(); a = [str(int(x)) for x in v[1:1+int(v[0])]]
    return str(max(int("".join(p)) for p in permutations(a)))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
