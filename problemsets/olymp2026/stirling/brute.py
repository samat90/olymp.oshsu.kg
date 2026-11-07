import sys

n, K = map(int, sys.stdin.read().split())
P = 998244353
S = [[0] * (K + 1) for _ in range(n + 1)]
S[0][0] = 1
for i in range(1, n + 1):
    for k in range(1, K + 1):
        S[i][k] = (k * S[i - 1][k] + S[i - 1][k - 1]) % P
print(' '.join(str(S[n][k]) for k in range(1, K + 1)))
