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
    n = r.randint(1, 5) if t <= 3 else r.randint(7, 9)
    d = "".join(r.choice("0123456789") for _ in range(n))
    # цель — значение случайного выражения, чтобы ответ был ненулевым
    ops = [r.choice(["+", "-", "*", ""]) for _ in range(n-1)]
    e = d[0] + "".join(o + c for o, c in zip(ops, d[1:]))
    try:
        import re
        if re.search(r"(?<!\d)0\d", e): raise ValueError
        T_ = eval(e)
    except Exception: T_ = r.randint(-20, 100)
    if r.random() < 0.2: T_ += 1
    return d + "\n%d\n" % T_

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2124 * 1000 + t)
    sys.stdout.write(gen(r, t))
