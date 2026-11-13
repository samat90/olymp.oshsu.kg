import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, k = int(d[0]), int(d[1]); a = sorted(map(int, d[2:2+n]))
    g = [a[i+1]-a[i] for i in range(n-1)]
    lo, hi = 1, max(max(g), 1)
    while lo < hi:
        m = (lo+hi)//2
        if sum(max(0, (x+m-1)//m-1) for x in g) <= k: hi = m
        else: lo = m+1
    return str(lo)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
