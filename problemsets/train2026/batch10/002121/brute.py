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
    n = int(s)
    shapes = [[(0,0),(1,0)], [(0,0),(0,1)], [(0,0),(1,0),(0,1)], [(0,0),(0,1),(1,1)], [(0,0),(1,0),(1,1)], [(0,1),(1,0),(1,1)]]
    # клетки (строка, столбец); добавляем 4 уголка
    def go(filled):
        for c in range(n):
            for rr in range(2):
                if (rr, c) not in filled: first = (rr, c); break
            else: continue
            break
        else: return 1
        cnt = 0
        for sh in shapes:
            # якорь: первая по порядку (столбец, строка) клетка фигуры совпадает с first
            cells = sorted(((y, x) for x, y in sh))
            dx, dy = cells[0]
            pts = [(x - dy, y - dx + 0) for (y, x) in cells]
            pl = [(first[0] + (x - cells[0][1]), first[1] + (y - cells[0][0])) for (y, x) in cells]
            if all(0 <= a < 2 and 0 <= b < n and (a, b) not in filled for a, b in pl):
                cnt += go(filled | frozenset(pl))
        return cnt
    return go(frozenset()) % (10**9 + 7)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
