import sys
d = sys.stdin.read().split()
n = int(d[0])
c = [[int(d[1 + i * n + j]) for j in range(n)] for i in range(n)]
INF = float('inf')
dp = [INF] * (1 << n)
dp[0] = 0
for mask in range(1 << n):
    if dp[mask] == INF:
        continue
    i = bin(mask).count('1')
    if i == n:
        continue
    for j in range(n):
        if not mask >> j & 1 and c[i][j] >= 0:
            v = dp[mask] + c[i][j]
            if v < dp[mask | 1 << j]:
                dp[mask | 1 << j] = v
print(dp[-1] if dp[-1] < INF else -1)
