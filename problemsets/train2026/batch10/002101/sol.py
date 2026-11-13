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
    v = s.split(); n, m = int(v[0]), int(v[1]); g = v[2:2+n]
    h = [0]*(m+1); best = 0
    for i in range(n):
        row = g[i]
        for j in range(m): h[j] = h[j] + 1 if row[j] == '1' else 0
        st = [-1]
        for j in range(m+1):
            while len(st) > 1 and h[st[-1]] >= h[j]:
                top = st.pop(); area = h[top] * (j - st[-1] - 1)
                if area > best: best = area
            st.append(j)
    return best

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
