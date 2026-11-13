import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, W = int(d[0]), int(d[1]); a = sorted(map(int, d[2:2+n])); i, j, c = 0, n-1, 0
    while i <= j:
        if i < j and a[i]+a[j] <= W: i += 1
        j -= 1; c += 1
    return str(c)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
