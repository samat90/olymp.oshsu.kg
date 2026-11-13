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
    v = list(map(int, s.split()))
    (x1,y1,x2,y2,x3,y3), q = v[:6], v[6]
    o = []
    cr = lambda ax,ay,bx,by,px,py: (bx-ax)*(py-ay)-(by-ay)*(px-ax)
    for i in range(q):
        x, y = v[7+2*i], v[8+2*i]
        c = [cr(x1,y1,x2,y2,x,y), cr(x2,y2,x3,y3,x,y), cr(x3,y3,x1,y1,x,y)]
        if min(c) < 0 and max(c) > 0: o.append(0)
        elif 0 in c: o.append(2)
        else: o.append(1)
    return "\n".join(map(str, o))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
