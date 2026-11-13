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
    v = list(map(int, s.split())); n = v[0]; h = v[1:] + [0]
    st = []; best = 0
    for i, x in enumerate(h):
        start = i
        while st and st[-1][1] >= x:
            j, hh = st.pop(); best = max(best, hh * (i - j)); start = j
        st.append((start, x))
    return best

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
