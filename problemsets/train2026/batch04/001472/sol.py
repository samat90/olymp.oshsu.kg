import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, K = int(d[0]), int(d[1]); a = sorted(map(int, d[2:2+n])); r = 0
    for i in range(n):
        r += bisect_right(a, K-a[i], i+1) - bisect_left(a, K-a[i], i+1)
    return str(r)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
