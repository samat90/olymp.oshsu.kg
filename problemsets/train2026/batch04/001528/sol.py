import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, k = int(d[0]), int(d[1]); s = sorted((int(d[2+2*i]), int(d[3+2*i])) for i in range(n))
    cur = 0
    for l, r in s:
        if l > cur+1:
            free = l-cur-1
            if k <= free: return str(cur+k)
            k -= free
        cur = max(cur, r)
    return str(cur+k)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
