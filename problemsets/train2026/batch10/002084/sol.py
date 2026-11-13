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
    v = s.split(); n = int(v[0]); pat = v[1]; res = []; st = []
    for i in range(1, n+1):
        st.append(i)
        if i == n or pat[i-1] == 'I':
            while st: res.append(st.pop())
    return " ".join(map(str, res))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
