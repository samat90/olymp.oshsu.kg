import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, p = int(d[0]), int(d[1]); a = sorted(map(int, d[2:2+n]))
    lo, hi = 0, a[-1]-a[0]
    while lo < hi:
        m = (lo+hi)//2; c = 0; i = 0
        while i+1 < n:
            if a[i+1]-a[i] <= m: c += 1; i += 2
            else: i += 1
        if c >= p: hi = m
        else: lo = m+1
    return str(lo)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
