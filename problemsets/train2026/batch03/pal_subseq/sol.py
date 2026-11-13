import sys

def sol(inp):
    s = inp.split()[0]
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                dp[i][j] = dp[i + 1][j - 1] + 2 if i + 1 <= j - 1 else 2
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return str(dp[0][n - 1])


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
