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
    A, q = v[:6], v[6]
    ar = lambda a,b,c,d,e,f: abs((c-a)*(f-b)-(d-b)*(e-a))
    tot = ar(*A)
    o = []
    for i in range(q):
        x, y = v[7+2*i], v[8+2*i]
        a1 = ar(x,y,A[2],A[3],A[4],A[5]); a2 = ar(A[0],A[1],x,y,A[4],A[5]); a3 = ar(A[0],A[1],A[2],A[3],x,y)
        if a1+a2+a3 != tot: o.append(0)
        elif 0 in (a1,a2,a3): o.append(2)
        else: o.append(1)
    return "\n".join(map(str, o))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
