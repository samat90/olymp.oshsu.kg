import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); g = list(map(int, d[1:1+n])); c = list(map(int, d[1+n:1+2*n]))
    if sum(g) < sum(c): return '-1'
    t = 0; st_ = 0
    for i in range(n):
        t += g[i]-c[i]
        if t < 0: t = 0; st_ = i+1
    return str(st_+1)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
