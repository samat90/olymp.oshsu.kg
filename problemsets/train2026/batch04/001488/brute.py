import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    from itertools import combinations
    d = d.split(); n, k = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n])); best = 0
    for cuts in combinations(range(1, n), k):
        c = (0,) + cuts + (n,)
        best = max(best, min(sum(a[c[i]:c[i+1]]) for i in range(k+1)))
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
