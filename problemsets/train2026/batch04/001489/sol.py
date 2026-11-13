import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, m, k = int(d[0]), int(d[1]), int(d[2]); a = list(map(int, d[3:3+n]))
    if m*k > n: return '-1'
    lo, hi = min(a), max(a)
    while lo < hi:
        t = (lo+hi)//2; c = 0; r = 0
        for x in a:
            if x <= t:
                r += 1
                if r == k: c += 1; r = 0
            else: r = 0
        if c >= m: hi = t
        else: lo = t+1
    return str(lo)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
