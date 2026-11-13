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
    W = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    @lru_cache(None)
    def f(b, turn):
        # результат для X: 1 победа X, 0 ничья, -1 победа O
        for w in W:
            if b[w[0]] != '.' and b[w[0]] == b[w[1]] == b[w[2]]: return 1 if b[w[0]] == 'X' else -1
        if '.' not in b: return 0
        res = []
        for i in range(9):
            if b[i] == '.':
                res.append(f(b[:i] + turn + b[i+1:], 'O' if turn == 'X' else 'X'))
        return max(res) if turn == 'X' else min(res)
    o = []
    for i in range(T_):
        b = "".join(v[1+4*i:4+4*i]); turn = v[4+4*i]
        x = f(b, turn)
        o.append("X" if x == 1 else ("O" if x == -1 else "Ничья"))
    return "\n".join(o)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
