import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); q = int(d[0]); r = []
    for i in range(q):
        a, b, h = int(d[1+3*i]), int(d[2+3*i]), int(d[3+3*i])
        lo, hi = 1, h
        while lo < hi:
            m = (lo+hi)//2
            if (m-1)*(a-b)+a >= h: hi = m
            else: lo = m+1
        r.append(lo)
    return ' '.join(map(str, r))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
