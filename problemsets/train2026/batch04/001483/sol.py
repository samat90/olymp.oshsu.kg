import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, m = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n]))
    lo, hi = 0, min(a)*m
    while lo < hi:
        t = (lo+hi)//2
        if sum(t//x for x in a) >= m: hi = t
        else: lo = t+1
    return str(lo)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
