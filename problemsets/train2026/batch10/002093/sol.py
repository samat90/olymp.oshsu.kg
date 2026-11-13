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
    n = int(s); par = {1 % n: (-1, '1')}; q = deque([1 % n])
    while 0 not in par:
        x = q.popleft()
        for d in '01':
            y = (x*10 + int(d)) % n
            if y not in par: par[y] = (x, d); q.append(y)
    res = []; x = 0
    while x != -1:
        p, d = par[x]; res.append(d); x = p
    return "".join(reversed(res))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
