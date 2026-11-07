import sys

d = sys.stdin.read().split()
n = int(d[0])
a = [int(x) for x in d[1:1 + n]]
b = a + a
pre = [0]
for v in b:
    pre.append(pre[-1] + v)
best = None
for s in range(n):
    dp = [[0] * n for _ in range(n)]
    for ln in range(2, n + 1):
        for i in range(0, n - ln + 1):
            j = i + ln - 1
            dp[i][j] = min(dp[i][k] + dp[k + 1][j] for k in range(i, j)) + pre[s + j + 1] - pre[s + i]
    v = dp[0][n - 1]
    best = v if best is None else min(best, v)
print(best)
