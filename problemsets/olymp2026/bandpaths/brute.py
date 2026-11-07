import sys

d = sys.stdin.read().split()
T = int(d[0])
P = 1000000007
out = []
for t in range(T):
    N, h, a, b = (int(x) for x in d[1 + 4 * t:5 + 4 * t])
    dp = [0] * (h + 1)
    dp[a] = 1
    for _ in range(N):
        nd = [0] * (h + 1)
        for v in range(h + 1):
            if dp[v]:
                if v > 0:
                    nd[v - 1] = (nd[v - 1] + dp[v]) % P
                if v < h:
                    nd[v + 1] = (nd[v + 1] + dp[v]) % P
        dp = nd
    out.append(dp[b])
print('\n'.join(map(str, out)))
