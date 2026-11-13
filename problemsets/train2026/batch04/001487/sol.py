import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, k = int(d[0]), int(d[1]); a = sorted(map(int, d[2:2+n]))
    lo, hi = 0, a[-1]-a[0]
    while lo < hi:
        m = (lo+hi)//2; c = 0; j = 0
        for i in range(n):
            while a[i]-a[j] > m: j += 1
            c += i-j
        if c >= k: hi = m
        else: lo = m+1
    return str(lo)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
