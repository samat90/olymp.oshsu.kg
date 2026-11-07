import sys

d = sys.stdin.read().split()
P = 998244353
B, n, K, q = int(d[0]), int(d[1]), int(d[2]), int(d[3])
a = [int(x) for x in d[4:4 + n]]
S = 1 << B
dp = [0] * S
dp[0] = 1
for _ in range(K):
    nd = [0] * S
    for v in range(S):
        if dp[v]:
            for x in a:
                nd[v ^ x] = (nd[v ^ x] + dp[v]) % P
    dp = nd
print('\n'.join(str(dp[int(x)]) for x in d[4 + n:4 + n + q]))
