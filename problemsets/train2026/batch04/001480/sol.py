import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, k = int(d[0]), int(d[1]); a = sorted(map(int, d[2:2+n]))
    lo, hi = 1, a[-1]-a[0]
    while lo < hi:
        m = (lo+hi+1)//2; c = 1; last = a[0]
        for x in a:
            if x-last >= m: c += 1; last = x
        if c >= k: lo = m
        else: hi = m-1
    return str(lo)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
