import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, m, k = int(d[0]), int(d[1]), int(d[2]); a = list(map(int, d[3:3+n])); b = list(map(int, d[3+n:3+n+m]))
    lo, hi = 1, 10**9
    while lo < hi:
        mid = (lo+hi)//2
        if bisect_right(a, mid) + bisect_right(b, mid) >= k: hi = mid
        else: lo = mid+1
    return str(lo)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
