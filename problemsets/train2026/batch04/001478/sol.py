import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, X = int(d[0]), int(d[1]); a = sorted(map(int, d[2:2+n])); best = None
    for i in range(n-1):
        j = bisect_left(a, X-a[i], i+1)
        for jj in (j-1, j):
            if i < jj < n:
                s = a[i]+a[jj]; k = (abs(s-X), s)
                if best is None or k < best: best = k
    return str(best[1])

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
