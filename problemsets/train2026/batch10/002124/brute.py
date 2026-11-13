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
    d, T_ = s.split(); T_ = int(T_); n = len(d); cnt = 0
    for ops in product(["+", "-", "*", ""], repeat=n-1):
        e = d[0] + "".join(o + c for o, c in zip(ops, d[1:]))
        toks = re.findall(r"\d+", e)
        if any(len(x) > 1 and x[0] == '0' for x in toks): continue
        if eval(e) == T_: cnt += 1
    return cnt

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
