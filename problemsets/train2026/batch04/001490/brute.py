import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, k = int(d[0]), int(d[1]); a = sorted(map(int, d[2:2+n]))
    g = [a[i+1]-a[i] for i in range(n-1)]; best = None
    def rec(i, left, cur):
        nonlocal best
        if i == len(g):
            best = cur if best is None else min(best, cur); return
        for c in range(left+1): rec(i+1, left-c, max(cur, -(-g[i]//(c+1))))
    rec(0, k, 1)
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
