import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); r = list(map(int, d[1:1+n])); c = [1]*n
    for i in range(1, n):
        if r[i] > r[i-1]: c[i] = c[i-1]+1
    for i in range(n-2, -1, -1):
        if r[i] > r[i+1]: c[i] = max(c[i], c[i+1]+1)
    return str(sum(c))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
