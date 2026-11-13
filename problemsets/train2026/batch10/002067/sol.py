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
    import heapq
    v = list(map(int, s.split())); n, k = v[0], v[1]
    h = [0]*min(k, n); heapq.heapify(h); wait = 0; last = 0
    for i in range(n):
        a, d = v[2+2*i], v[3+2*i]
        f = heapq.heappop(h); st = max(a, f); wait += st - a
        heapq.heappush(h, st + d); last = max(last, st + d)
    return "%d %d" % (wait, last)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
