import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, Ln = int(d[0]), int(d[1]); s = sorted((int(d[2+2*i]), int(d[3+2*i])) for i in range(n)); cur = 0; free = 0
    for l, r in s:
        if l > cur: free += l-cur
        cur = max(cur, r)
    return str(free + Ln - cur)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
