import sys

d = sys.stdin.read().split()
n = int(d[0])
x = [int(v) for v in d[1:1 + n]]
s = [int(v) for v in d[1 + n:1 + 2 * n]]
dp = [0] * n
dp[0] = s[0]
for j in range(1, n):
    dp[j] = s[j] + min(dp[i] + (x[j] - x[i]) ** 2 for i in range(j))
print(dp[-1])
