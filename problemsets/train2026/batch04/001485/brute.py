import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    n, m, k = map(int, d.split())
    return str(sorted(i*j for i in range(1, n+1) for j in range(1, m+1))[k-1])

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
