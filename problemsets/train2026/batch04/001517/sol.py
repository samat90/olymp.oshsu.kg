import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, ln = int(d[0]), int(d[1]); a = sorted(map(int, d[2:2+n])); c = 0; i = 0
    while i < n:
        c += 1; e = a[i]+ln
        while i < n and a[i] <= e: i += 1
    return str(c)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
