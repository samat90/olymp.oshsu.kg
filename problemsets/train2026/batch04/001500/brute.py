import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); j = [(int(d[1+2*i]), int(d[2+2*i])) for i in range(n)]; best = 0
    for m in range(1 << n):
        c = sorted(j[i] for i in range(n) if m >> i & 1)
        if all(c[i][0] >= i+1 for i in range(len(c))): best = max(best, sum(p for _, p in c))
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
