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
    n = N(r, t, 5, 1000000)
    a = list(range(1, n+1))
    if r.random() < 0.5 or t == 0:
        # стек-сортируемая: симуляция случайных операций
        res = []; st = []; nxt = 1; src = list(range(1, n+1)); b = []
        # построим, пропуская номера в обратном порядке
        order = list(range(1, n+1)); r.shuffle(order)
        # пусть стек-сортируемая получится из случайного вывода: генерируем push/pop
        res = []; st = []; cnt = 0; items = []
        # items — входная последовательность; на выходе должны получиться 1..n
        # обратная конструкция: идём по выходу 1..n и решаем, что вошло
        free = []
        pos = list(range(n))
        # используем простой способ: случайная стек-сортируемая перестановка как результат стек-перестановки тождественной
        out = []; st = []; i = 1
        while len(out) < n:
            if st and (i > n or r.random() < 0.5): out.append(st.pop())
            else: st.append(i); i += 1
        # out — перестановка, получаемая из 1..n через стек; обратная к ней стек-сортируется
        inv = [0]*n
        for idx, x in enumerate(out): inv[x-1] = idx + 1
        a = inv
        if t >= 4 and r.random() < 0.5 and n > 2:
            i, j = r.sample(range(n), 2); a[i], a[j] = a[j], a[i]
    else:
        r.shuffle(a)
    return "%d\n" % n + " ".join(map(str, a)) + "\n"

if __name__ == '__main__':
    t = int(sys.argv[1])
    r = random.Random(2077 * 1000 + t)
    sys.stdout.write(gen(r, t))
