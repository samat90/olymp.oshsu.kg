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
    a = r.choice(["ab", "a", "abc", "ba"])
    n = r.randint(1, 5) if t <= 3 else r.randint(1500, 3000)
    m = r.randint(1, 5) if t <= 3 else r.randint(1500, 3000)
    if t == 10: n = m = 3000
    if t in (7, 8): return "a"*n + "\n" + "a"*m + "\n"
    return "".join(r.choice(a) for _ in range(n)) + "\n" + "".join(r.choice(a) for _ in range(m)) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2087 * 1000 + t)
    sys.stdout.write(gen(r, t))
