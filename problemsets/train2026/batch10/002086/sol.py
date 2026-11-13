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
    d, k = s.split(); k = int(k); K = k; st = []
    for c in d:
        while k and st and st[-1] > c: st.pop(); k -= 1
        st.append(c)
    if k: st = st[:len(st)-k]
    return "".join(st).lstrip("0") or "0"

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
