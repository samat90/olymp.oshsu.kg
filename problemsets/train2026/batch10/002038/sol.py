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
    cr = lambda ax,ay,bx,by,cx,cy: (bx-ax)*(cy-ay)-(by-ay)*(cx-ax)
    sg = lambda x: (x > 0) - (x < 0)
    def on(ax,ay,bx,by,px,py): return min(ax,bx) <= px <= max(ax,bx) and min(ay,by) <= py <= max(ay,by)
    for i in range(T_):
        ax,ay,bx,by,cx,cy,dx,dy = v[1+8*i:9+8*i]
        d1 = sg(cr(ax,ay,bx,by,cx,cy)); d2 = sg(cr(ax,ay,bx,by,dx,dy))
        d3 = sg(cr(cx,cy,dx,dy,ax,ay)); d4 = sg(cr(cx,cy,dx,dy,bx,by))
        ok = False
        if d1*d2 < 0 and d3*d4 < 0: ok = True
        elif d1 == 0 and on(ax,ay,bx,by,cx,cy): ok = True
        elif d2 == 0 and on(ax,ay,bx,by,dx,dy): ok = True
        elif d3 == 0 and on(cx,cy,dx,dy,ax,ay): ok = True
        elif d4 == 0 and on(cx,cy,dx,dy,bx,by): ok = True
        o.append("YES" if ok else "NO")
    return "\n".join(o)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
