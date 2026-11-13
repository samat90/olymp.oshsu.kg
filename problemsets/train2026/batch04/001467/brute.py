import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, m, k = int(d[0]), int(d[1]), int(d[2])
    return str(sorted(map(int, d[3:3+n+m]))[k-1])

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
