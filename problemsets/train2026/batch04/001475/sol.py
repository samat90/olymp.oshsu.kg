import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); q = int(d[0]); r = []
    def z(n):
        c = 0
        while n: n //= 5; c += n
        return c
    for k in map(int, d[1:1+q]):
        lo, hi = 0, 5*k
        while lo < hi:
            m = (lo+hi)//2
            if z(m) >= k: hi = m
            else: lo = m+1
        r.append(lo)
    return ' '.join(map(str, r))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
