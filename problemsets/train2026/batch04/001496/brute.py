import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    from itertools import combinations
    d = d.split(); n = int(d[0]); s = [(int(d[1+2*i]), int(d[2+2*i])) for i in range(n)]
    pts = sorted({x for p in s for x in p})
    for k in range(1, n+1):
        for c in combinations(pts, k):
            if all(any(l <= x <= r for x in c) for l, r in s): return str(k)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
