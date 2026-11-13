import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, Ln, C = int(d[0]), int(d[1]), int(d[2]); p = sorted(map(int, d[3:3+n]))
    pos = 0; stops = 0; i = 0
    while Ln - pos > C:
        best = None
        while i < n and p[i] <= pos + C: best = p[i]; i += 1
        if best is None: return '-1'
        pos = best; stops += 1
    return str(stops)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
