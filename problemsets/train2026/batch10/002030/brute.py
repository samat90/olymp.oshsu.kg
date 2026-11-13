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
    v = s.split(); t = int(v[0]); o = []
    for i in range(t):
        x1,y1,x2,y2,x3,y3 = map(int, v[1+6*i:7+6*i])
        d = lambda a,b,c,e: (a-c)**2+(b-e)**2
        q = sorted([d(x1,y1,x2,y2), d(x2,y2,x3,y3), d(x1,y1,x3,y3)])
        if (x1*(y2-y3)+x2*(y3-y1)+x3*(y1-y2)) == 0: o.append("Вырожденный")
        elif q[0]+q[1] == q[2]: o.append("Прямоугольный")
        elif q[0]+q[1] < q[2]: o.append("Тупоугольный")
        else: o.append("Остроугольный")
    return "\n".join(o)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
