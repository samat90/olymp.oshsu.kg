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
    d, T_ = s.split(); T_ = int(T_); n = len(d)
    def rec(i, total, last, op):
        # разбираем число, начинающееся в позиции i; op — оператор перед ним
        res = 0
        for j in range(i+1, n+1):
            if j - i > 1 and d[i] == '0': break
            x = int(d[i:j])
            if op == '+': nt, nl = total + last, x
            elif op == '-': nt, nl = total + last, -x
            else: nt, nl = total, last * x
            if j == n: res += 1 if nt + nl == T_ else 0
            else:
                for o in "+-*": res += rec(j, nt, nl, o)
        return res
    return rec(0, 0, 0, '+')

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
