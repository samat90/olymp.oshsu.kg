import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); p = list(map(int, d[1:1+n]))
    m = -1; c = 0
    for i in range(n):
        m = max(m, p[i])
        if m == i: c += 1
    return str(c)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
