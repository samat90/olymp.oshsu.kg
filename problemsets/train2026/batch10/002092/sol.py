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
    n = int(s); a = [0]*(n+1); res = []
    def db(t, p):
        if t > n:
            if n % p == 0: res.extend(a[1:p+1])
        else:
            a[t] = a[t-p]; db(t+1, p)
            for j in range(a[t-p]+1, 2):
                a[t] = j; db(t+1, t)
    db(1, 1)
    return "".join(map(str, res))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
