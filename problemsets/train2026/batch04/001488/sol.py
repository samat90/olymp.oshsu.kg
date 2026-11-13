import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, k = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n]))
    lo, hi = 0, sum(a)//(k+1)
    while lo < hi:
        m = (lo+hi+1)//2; c = 0; s = 0
        for x in a:
            s += x
            if s >= m: c += 1; s = 0
        if c >= k+1: lo = m
        else: hi = m-1
    return str(lo)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
