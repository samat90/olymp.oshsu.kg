import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n = int(d[0]); a = list(map(int, d[1:1+n])); INF = 10**9
    dp = [INF]*n; dp[0] = 0
    for i in range(n):
        if dp[i] == INF: continue
        for j in range(i+1, min(n, i+a[i]+1)): dp[j] = min(dp[j], dp[i]+1)
    return str(dp[-1]) if dp[-1] < INF else '-1'

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
