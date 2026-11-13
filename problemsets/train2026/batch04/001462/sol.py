import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, k = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n]))
    lo, hi = 0, n
    while lo < hi:
        m = (lo+hi)//2
        if a[m]-(m+1) >= k: hi = m
        else: lo = m+1
    return str(lo+k)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
