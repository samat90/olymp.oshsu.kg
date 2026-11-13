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
    v = s.split(); T_ = int(v[0])
    def winner(b):
        for a, c, d in [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]:
            if b[a] != '.' and b[a] == b[c] == b[d]: return b[a]
        return None
    def play(b, turn):
        w = winner(b)
        if w: return 1 if w == 'X' else -1
        if '.' not in b: return 0
        vals = []
        for i in range(9):
            if b[i] == '.':
                nb = list(b); nb[i] = turn
                vals.append(play(nb, 'O' if turn == 'X' else 'X'))
        return max(vals) if turn == 'X' else min(vals)
    o = []
    for i in range(T_):
        b = list("".join(v[1+4*i:4+4*i])); x = play(b, v[4+4*i])
        o.append({1: "X", -1: "O", 0: "Ничья"}[x])
    return "\n".join(o)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
