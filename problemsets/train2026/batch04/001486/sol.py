import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, Ln = int(d[0]), int(d[1]); p = sorted(map(int, d[2:2+n]))
    r = max(p[0], Ln-p[-1])
    for i in range(n-1): r = max(r, (p[i+1]-p[i]+1)//2)
    return str(r)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
