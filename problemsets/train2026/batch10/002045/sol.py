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
    v = list(map(int, s.split())); n = v[0]
    ev = []
    for i in range(n):
        l, r_, h = v[1+3*i:4+3*i]
        ev.append((l, -h, r_)); ev.append((r_, 0, 0))
    ev.sort()
    hp = []; res = []; cur = 0
    i = 0; m = len(ev)
    while i < m:
        x = ev[i][0]
        while i < m and ev[i][0] == x:
            if ev[i][1] != 0: heapq.heappush(hp, (ev[i][1], ev[i][2]))
            i += 1
        while hp and hp[0][1] <= x: heapq.heappop(hp)
        nh = -hp[0][0] if hp else 0
        if nh != cur:
            res.append((x, nh)); cur = nh
    return "%d\n" % len(res) + "\n".join("%d %d" % p for p in res)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
