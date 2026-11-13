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
    v = list(map(int, s.split())); n, p = v[0], v[1] - 1; a = v[2:2+n]
    cnt = [0]*10
    for x in a: cnt[x] += 1
    dq = deque((x, i) for i, x in enumerate(a)); printed = 0
    top = 9
    while True:
        while cnt[top] == 0: top -= 1
        x, i = dq.popleft()
        if x == top:
            printed += 1; cnt[x] -= 1
            if i == p: return printed
        else: dq.append((x, i))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
