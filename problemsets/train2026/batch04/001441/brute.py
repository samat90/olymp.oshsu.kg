import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    from collections import deque
    d = d.split(); n = int(d[0]); p = tuple(int(x) for x in d[1:1+n]); goal = tuple(range(1, n+1))
    dist = {p: 0}; q = deque([p])
    while q:
        c = q.popleft()
        if c == goal: return str(dist[c])
        for i in range(n):
            for j in range(i+1, n):
                l = list(c); l[i], l[j] = l[j], l[i]; t = tuple(l)
                if t not in dist: dist[t] = dist[c]+1; q.append(t)

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
