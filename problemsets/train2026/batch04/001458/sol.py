import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); q = int(d[0]); r = []
    for x in map(int, d[1:1+q]):
        lo, hi = 0, 10**9+1
        while hi-lo > 1:
            m = (lo+hi)//2
            if m*m <= x: lo = m
            else: hi = m
        r.append(lo)
    return ' '.join(map(str, r))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
