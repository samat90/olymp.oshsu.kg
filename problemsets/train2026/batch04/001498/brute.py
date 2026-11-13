import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, W = int(d[0]), int(d[1]); a = list(map(int, d[2:2+n])); INF = 10**9
    dp = [INF]*(1 << n); dp[0] = 0
    for m in range(1 << n):
        if dp[m] == INF: continue
        i = next((i for i in range(n) if not m >> i & 1), None)
        if i is None: continue
        dp[m | 1 << i] = min(dp[m | 1 << i], dp[m]+1)
        for j in range(i+1, n):
            if not m >> j & 1 and a[i]+a[j] <= W: dp[m | 1 << i | 1 << j] = min(dp[m | 1 << i | 1 << j], dp[m]+1)
    return str(dp[-1])

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
