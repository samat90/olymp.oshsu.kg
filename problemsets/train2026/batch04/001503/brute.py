import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    from itertools import combinations
    d = d.split(); n, Ln, C = int(d[0]), int(d[1]), int(d[2]); p = sorted(map(int, d[3:3+n]))
    for k in range(n+1):
        for c in combinations(p, k):
            pts = [0]+list(c)+[Ln]
            if all(pts[i+1]-pts[i] <= C for i in range(len(pts)-1)): return str(k)
    return '-1'

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
