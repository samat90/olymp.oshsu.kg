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
    k, n = map(int, s.split()); res = []; cur = []
    def go(start, rest):
        if len(cur) == k:
            if rest == 0: res.append(" ".join(map(str, cur)))
            return
        for x in range(start, 10):
            if x > rest: break
            cur.append(x); go(x+1, rest-x); cur.pop()
    go(1, n)
    return "\n".join([str(len(res))] + res)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
