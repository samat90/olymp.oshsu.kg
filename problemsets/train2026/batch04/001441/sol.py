import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); p = [int(x)-1 for x in d[1:1+n]]
    seen = [False]*n; c = 0
    for i in range(n):
        if not seen[i]:
            c += 1; j = i
            while not seen[j]: seen[j] = True; j = p[j]
    return str(n - c)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
