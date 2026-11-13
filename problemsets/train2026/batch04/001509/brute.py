import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, k = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n]))
    def rec(a, k):
        if k == 0: return sum(a)
        best = None
        for i in range(n):
            a[i] = -a[i]; r = rec(a, k-1); a[i] = -a[i]
            best = r if best is None else max(best, r)
        return best
    return str(rec(a, k))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
