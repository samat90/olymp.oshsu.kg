import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, k = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n]))
    lo, hi = 0, sum(a)//k
    while lo < hi:
        t = (lo+hi+1)//2
        if sum(min(x, t) for x in a) >= t*k: lo = t
        else: hi = t-1
    return str(lo)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
