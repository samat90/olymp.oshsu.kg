import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, m = int(d[0]), int(d[1])
    A = [(int(d[2+2*i]), int(d[3+2*i])) for i in range(n)]; o = 2+2*n
    B = [(int(d[o+2*i]), int(d[o+1+2*i])) for i in range(m)]
    br = sorted(r for l, r in B); bl = sorted(l for l, r in B); c = 0
    for l, r in A: c += bisect_left(br, l) + (m - bisect_right(bl, r))
    return str(n*m - c)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
