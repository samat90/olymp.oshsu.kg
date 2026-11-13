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
    v = s.split("\n"); S = v[0].strip(); k = int(v[1]); st = []
    for c in S:
        if st and st[-1][0] == c:
            st[-1][1] += 1
            if st[-1][1] == k: st.pop()
        else: st.append([c, 1])
    return "".join(c * q for c, q in st)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
