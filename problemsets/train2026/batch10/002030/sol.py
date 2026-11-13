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
        if (x2-x1)*(y3-y1) - (y2-y1)*(x3-x1) == 0: o.append("Вырожденный"); continue
        dots = [(x2-x1)*(x3-x1)+(y2-y1)*(y3-y1), (x1-x2)*(x3-x2)+(y1-y2)*(y3-y2), (x1-x3)*(x2-x3)+(y1-y3)*(y2-y3)]
        if 0 in dots: o.append("Прямоугольный")
        elif min(dots) < 0: o.append("Тупоугольный")
        else: o.append("Остроугольный")
    return "\n".join(o)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
