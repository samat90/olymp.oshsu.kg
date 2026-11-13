import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    n, m, k = map(int, d.split())
    lo, hi = 1, n*m
    while lo < hi:
        x = (lo+hi)//2
        if sum(min(m, x//i) for i in range(1, n+1)) >= k: hi = x
        else: lo = x+1
    return str(lo)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
