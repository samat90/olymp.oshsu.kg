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
    v = s.split(); n, m, k = int(v[0]), int(v[1]), int(v[2])
    live = {(i, j) for i in range(n) for j in range(m) if v[3+i][j] == '#'}
    for _ in range(k):
        cnt = Counter()
        for (i, j) in live:
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if di or dj: cnt[((i+di) % n, (j+dj) % m)] += 1
        live = {c for c in cnt if cnt[c] == 3 or (c in live and cnt[c] == 2)}
    return "\n".join("".join('#' if (i, j) in live else '.' for j in range(m)) for i in range(n))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
