import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    t = list(map(int, s.split())); n, K = t[:2]; a = t[2:2 + n]
    dp = [0] * n; dq = deque(); best = -10**18
    for i in range(n):
        dp[i] = a[i] + (max(0, dp[dq[0]]) if dq else 0)
        best = max(best, dp[i])
        while dq and dp[dq[-1]] <= dp[i]: dq.pop()
        dq.append(i)
        if dq[0] <= i - K: dq.popleft()
    return str(best)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
