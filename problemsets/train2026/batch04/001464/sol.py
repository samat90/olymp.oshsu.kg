import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n])); lo, hi = 0, n//2
    while lo < hi:
        m = (lo+hi)//2
        if a[2*m] == a[2*m+1]: lo = m+1
        else: hi = m
    return str(a[2*lo])

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
