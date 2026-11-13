import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, Ln = int(d[0]), int(d[1]); s = sorted((int(d[2+2*i]), int(d[3+2*i])) for i in range(n))
    i = 0; cur = 0; c = 0
    while cur < Ln:
        best = cur
        while i < n and s[i][0] <= cur: best = max(best, s[i][1]); i += 1
        if best == cur: return '-1'
        cur = best; c += 1
    return str(c)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
