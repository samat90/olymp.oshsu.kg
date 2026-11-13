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
    v = list(map(int, s.split())); T_ = v[0]; o = []
    for i in range(T_):
        ax,ay,bx,by,cx,cy,dx,dy = v[1+8*i:9+8*i]
        rx, ry, sx, sy = bx-ax, by-ay, dx-cx, dy-cy
        den = rx*sy - ry*sx
        qx, qy = cx-ax, cy-ay
        if den != 0:
            tt = Fraction(qx*sy - qy*sx, den); uu = Fraction(qx*ry - qy*rx, den)
            ok = 0 <= tt <= 1 and 0 <= uu <= 1
        elif qx*ry - qy*rx != 0: ok = False
        else:
            rr = rx*rx + ry*ry
            t0 = Fraction(qx*rx + qy*ry, rr); t1 = Fraction((dx-ax)*rx + (dy-ay)*ry, rr)
            lo, hi = min(t0, t1), max(t0, t1)
            ok = lo <= 1 and hi >= 0
        o.append("YES" if ok else "NO")
    return "\n".join(o)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
