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
    n = int(s); full = (1 << n) - 1; res = []
    def go(cols, d1, d2):
        if cols == full: return True
        free = full & ~(cols | d1 | d2)
        while free:
            b = free & -free; free ^= b
            res.append(b.bit_length())
            if go(cols | b, ((d1 | b) << 1) & full, (d2 | b) >> 1): return True
            res.pop()
        return False
    return " ".join(map(str, res)) if go(0, 0, 0) else "-1"

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
