import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, m = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n])); b = sorted(map(int, d[2+n:2+n+m])); best = 10**18
    for x in a:
        i = bisect_left(b, x)
        if i < m: best = min(best, b[i]-x)
        if i > 0: best = min(best, x-b[i-1])
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
