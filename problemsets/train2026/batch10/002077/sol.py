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
    v = list(map(int, s.split())); n = v[0]; st = []; nxt = 1
    for x in v[1:]:
        st.append(x)
        while st and st[-1] == nxt: st.pop(); nxt += 1
    return "YES" if nxt == n+1 else "NO"

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
