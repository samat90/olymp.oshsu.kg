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
    M = 4 if t <= 3 else 10**6
    while True:
        p = [r.randint(-M, M) for _ in range(6)]
        if (p[2]-p[0])*(p[5]-p[1]) - (p[3]-p[1])*(p[4]-p[0]) != 0: break
    q = N(r, t, 6, 100000)
    out = [" ".join(map(str, p)), str(q)]
    for _ in range(q):
        if t > 3 and r.random() < 0.3:
            # point on a side or a vertex
            i = r.randrange(3); a = (p[2*i], p[2*i+1]); b = (p[(2*i+2)%6], p[(2*i+3)%6])
            k = r.randint(0, 4)
            x = a[0] + (b[0]-a[0]) * k // 4; y = a[1] + (b[1]-a[1]) * k // 4
            if (b[0]-a[0]) * k % 4 or (b[1]-a[1]) * k % 4: x, y = a
            out.append("%d %d" % (x, y))
        else:
            out.append("%d %d" % (r.randint(-M, M), r.randint(-M, M)))
    return "\n".join(out) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2031 * 1000 + t)
    sys.stdout.write(gen(r, t))
