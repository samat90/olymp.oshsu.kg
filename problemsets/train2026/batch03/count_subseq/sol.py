import sys

def sol(inp):
    s, t = inp.split()[:2]
    M = 10 ** 9 + 7
    dp = [0] * (len(t) + 1)
    dp[0] = 1
    for c in s:
        for j in range(len(t), 0, -1):
            if t[j - 1] == c:
                dp[j] = (dp[j] + dp[j - 1]) % M
    return str(dp[len(t)])


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
