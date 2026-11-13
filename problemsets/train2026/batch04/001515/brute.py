import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n])); V = max(a)+n+1
    INF = 10**18; dp = {v: v-a[0] for v in range(a[0], V+1)}
    for i in range(1, n):
        nd = {}
        for v in range(a[i], V+1):
            best = min((c for u, c in dp.items() if u < v), default=INF)
            if best < INF: nd[v] = best+v-a[i]
        dp = nd
    return str(min(dp.values()))

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
