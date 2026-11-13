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
    v = s.split(); a = v[1:1+int(v[0])]
    a.sort(key=cmp_to_key(lambda x, y: -1 if x+y > y+x else (1 if x+y < y+x else 0)))
    r = "".join(a).lstrip("0")
    return r or "0"

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
