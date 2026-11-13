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
    g = s.strip(); n = len(g)
    L = ["0", "1"]
    for _ in range(n-1): L = ["0"+x for x in L] + ["1"+x for x in reversed(L)]
    i = L.index(g)
    return format(i, "0%db" % n)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
