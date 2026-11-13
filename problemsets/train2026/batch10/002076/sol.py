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
    s = s.strip(); front = deque(); cur = []; home = False
    # cur — текущий блок, который пишется перед курсором; home=True — блок идёт в начало
    parts_front = []; parts_back = []
    mode = 'back'; buf = []
    for c in s:
        if c == '[' or c == ']':
            if buf:
                (parts_front if mode == 'front' else parts_back).append("".join(buf)); buf = []
            mode = 'front' if c == '[' else 'back'
        else: buf.append(c)
    if buf: (parts_front if mode == 'front' else parts_back).append("".join(buf))
    return "".join(reversed(parts_front)) + "".join(parts_back)

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
