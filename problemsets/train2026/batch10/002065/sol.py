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
    LOG = n.bit_length()
    tree = [0]*(n+1)
    for i in range(1, n+1):
        tree[i] += 1
        j = i + (i & -i)
        if j <= n: tree[j] += tree[i]
    def kth(q):
        pos = 0
        for b in range(LOG, -1, -1):
            np_ = pos + (1 << b)
            if np_ <= n and tree[np_] < q:
                pos = np_; q -= tree[np_]
        return pos + 1
    out = []; cur = 0; m = n
    for _ in range(n):
        cur = (cur + k - 1) % m
        p = kth(cur + 1); out.append(p)
        i = p
        while i <= n: tree[i] -= 1; i += i & -i
        m -= 1
        if m: cur %= m
    return " ".join(map(str, out))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
