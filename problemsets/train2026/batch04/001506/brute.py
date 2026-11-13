import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); r = list(map(int, d[1:1+n])); c = [1]*n; ch = True
    while ch:
        ch = False
        for i in range(n):
            for j in (i-1, i+1):
                if 0 <= j < n and r[i] > r[j] and c[i] <= c[j]: c[i] = c[j]+1; ch = True
    return str(sum(c))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
