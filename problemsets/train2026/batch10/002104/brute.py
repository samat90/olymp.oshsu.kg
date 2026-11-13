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
    v = list(map(int, s.split())); n = v[0]
    a = [v[1+i*n:1+(i+1)*n] for i in range(n)]
    def det(M):
        k = len(M)
        if k == 1: return M[0][0]
        return sum((-1)**j * M[0][j] * det([row[:j] + row[j+1:] for row in M[1:]]) for j in range(k))
    return det(a) % (10**9 + 7)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
