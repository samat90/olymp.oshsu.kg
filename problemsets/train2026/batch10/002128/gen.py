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
    n = r.randint(1, 3) if t <= 3 else r.randint(3, 4); m = r.randint(1, 3) if t <= 3 else (4 if t == 10 else r.randint(3, 4))
    al = r.choice(["ab", "abc", "abcd"]) if t != 10 else "ab"
    g = ["".join(r.choice(al) for _ in range(m)) for _ in range(n)]
    q = r.randint(1, 8) if t <= 3 else 50
    words = []
    for _ in range(q):
        if r.random() < 0.5:
            i, j = r.randrange(n), r.randrange(m); w = g[i][j]
            for _ in range(r.randint(0, 9)):
                nb = [(a, b) for a, b in ((i+1, j), (i-1, j), (i, j+1), (i, j-1)) if 0 <= a < n and 0 <= b < m]
                if not nb: break
                i, j = r.choice(nb); w += g[i][j]
            if r.random() < 0.3: w = w[:-1] + r.choice(al + "e")
        else: w = "".join(r.choice(al) for _ in range(r.randint(1, 10 if t > 3 else 5)))
        words.append(w)
    return "%d %d\n" % (n, m) + "\n".join(g) + "\n%d\n" % q + "\n".join(words) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2128 * 1000 + t)
    sys.stdout.write(gen(r, t))
