import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, k = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n]))
    lo, hi = max(a), sum(a)
    while lo < hi:
        m = (lo+hi)//2; c = 1; s = 0
        for x in a:
            if s+x > m: c += 1; s = x
            else: s += x
        if c <= k: hi = m
        else: lo = m+1
    return str(lo)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
