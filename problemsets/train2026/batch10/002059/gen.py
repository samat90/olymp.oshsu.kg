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

def N(r, t, tiny, big):
    if t == 0: return r.randint(1, tiny)
    if t == 10: return big
    if t <= 3: return r.randint(1, tiny * 2)
    return max(1, big * t * t // 100)


def gen(r, t):
    T_ = N(r, t, 3, 2000)
    lines = [str(T_)]
    W = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    def win(b, c): return any(all(b[i] == c for i in w) for w in W)
    for _ in range(T_):
        while True:
            b = ['.']*9; turn = 'X'; k = r.randint(3 if t == 0 else 0, 8)
            ok = True
            for _ in range(k):
                e = [i for i in range(9) if b[i] == '.']
                i = r.choice(e); b[i] = turn
                if win(b, turn): ok = False; break
                turn = 'O' if turn == 'X' else 'X'
            if ok and '.' in b: break
        lines += ["".join(b[0:3]), "".join(b[3:6]), "".join(b[6:9]), turn]
    return "\n".join(lines) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2059 * 1000 + t)
    sys.stdout.write(gen(r, t))
