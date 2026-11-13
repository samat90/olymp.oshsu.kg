import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    from itertools import combinations
    d = d.split(); n, k = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n])); best = None
    for cuts in combinations(range(1, n), k-1):
        c = (0,) + cuts + (n,)
        m = max(sum(a[c[i]:c[i+1]]) for i in range(k))
        best = m if best is None else min(best, m)
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
