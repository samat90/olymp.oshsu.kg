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
    n, k = map(int, s.split())
    # f[i][b] — число способов дописать i символов при балансе b
    f = [[0]*(2*n+2) for _ in range(2*n+1)]
    f[0][0] = 1
    for i in range(1, 2*n+1):
        for b in range(0, 2*n+1):
            f[i][b] = (f[i-1][b+1] if b+1 <= 2*n else 0) + (f[i-1][b-1] if b > 0 else 0)
    res = []; b = 0
    for pos in range(2*n):
        rest = 2*n - pos - 1
        c = f[rest][b+1]
        if k <= c: res.append('('); b += 1
        else: k -= c; res.append(')'); b -= 1
    return "".join(res)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
