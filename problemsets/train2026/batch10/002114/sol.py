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
    c = Counter(s.strip()); n = sum(c.values()); res = []; cur = []
    def go():
        if len(cur) == n: res.append("".join(cur)); return
        for ch in sorted(c):
            if c[ch]:
                c[ch] -= 1; cur.append(ch); go(); cur.pop(); c[ch] += 1
    go()
    return "\n".join(res)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
