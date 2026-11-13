import sys
from bisect import bisect_left, bisect_right
from collections import Counter, deque
import heapq, itertools, functools

def solve(d):
    d = d.split(); n, ln = int(d[0]), int(d[1]); a = sorted(map(int, d[2:2+n])); INF = 10**9
    dp = [0]+[INF]*n
    for i in range(1, n+1):
        for j in range(i):
            if a[i-1]-a[j] <= ln: dp[i] = min(dp[i], dp[j]+1)
    return str(dp[n])

if __name__ == "__main__":
    sys.stdout.write(str(solve(sys.stdin.read())).rstrip() + "\n")
