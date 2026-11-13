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
    v = s.split(); n, m = int(v[0]), int(v[1]); g = [bytearray(x, 'ascii') for x in v[2:2+n]]; c = 0
    for i in range(n):
        for j in range(m):
            if g[i][j] == 49:
                c += 1; g[i][j] = 48; st = [(i, j)]
                while st:
                    x, y = st.pop()
                    for a, b in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                        if 0 <= a < n and 0 <= b < m and g[a][b] == 49:
                            g[a][b] = 48; st.append((a, b))
    return c

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
