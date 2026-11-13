import sys

def sol(inp):
    s = inp.split()[0]
    n = len(s)
    pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            if s[i] == s[j] and (j - i < 2 or pal[i + 1][j - 1]):
                pal[i][j] = True
    dp = [0] * n
    for j in range(n):
        if pal[0][j]:
            dp[j] = 0
        else:
            dp[j] = min(dp[i - 1] + 1 for i in range(1, j + 1) if pal[i][j])
    return str(dp[n - 1])


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
