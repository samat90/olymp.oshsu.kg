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

def N(r, t, tiny, big):
    if t == 0: return r.randint(1, tiny)
    if t == 10: return big
    if t <= 3: return r.randint(1, tiny * 2)
    return max(1, big * t * t // 100)


def gen(r, t):
    n = r.randint(1, 3) if t <= 3 else r.randint(4, 5); m = r.randint(2, 3) if t <= 3 else (5 if t == 10 else r.randint(4, 5))
    if t == 10: n = 5
    while True:
        g = [[('#' if r.random() < (0.3 if t <= 3 else 0.12) else '.') for _ in range(m)] for _ in range(n)]
        cells = [(i, j) for i in range(n) for j in range(m) if g[i][j] == '.']
        if len(cells) >= 2 and (t > 0 or len(cells) <= 8): break
    a, b = r.sample(cells, 2); g[a[0]][a[1]] = 'S'; g[b[0]][b[1]] = 'E'
    return "%d %d\n" % (n, m) + "\n".join("".join(row) for row in g) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2127 * 1000 + t)
    sys.stdout.write(gen(r, t))
