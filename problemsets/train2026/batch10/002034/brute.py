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
    v = list(map(int, s.split())); n = v[0]
    P = [(v[1+2*i], v[2+2*i]) for i in range(n)]
    if n < 3: return 0
    cr = lambda o,a,b: (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    st = min(P); cur = st; H = [st]
    while True:
        nx = None
        for q in P:
            if q == cur: continue
            if nx is None: nx = q; continue
            c = cr(cur, nx, q)
            if c < 0 or (c == 0 and (q[0]-cur[0])**2+(q[1]-cur[1])**2 > (nx[0]-cur[0])**2+(nx[1]-cur[1])**2): nx = q
        if nx == st or nx is None: break
        H.append(nx); cur = nx
        if len(H) > n + 2: break
    m = len(H)
    return abs(sum(H[i][0]*H[(i+1)%m][1] - H[(i+1)%m][0]*H[i][1] for i in range(m)))

if __name__ == '__main__':
    print(solve(sys.stdin.read()))
