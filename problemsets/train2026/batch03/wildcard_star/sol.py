import sys

def sol(inp):
    s, p = inp.split()[:2]
    n, m = len(s), len(p)
    dp = [False] * (n + 1)
    dp[0] = True
    for j in range(1, m + 1):
        c = p[j - 1]
        new = [False] * (n + 1)
        if c == '*':
            new[0] = dp[0]
            for i in range(1, n + 1):
                new[i] = dp[i] or new[i - 1]
        else:
            for i in range(1, n + 1):
                if dp[i - 1] and (c == '?' or c == s[i - 1]):
                    new[i] = True
        dp = new
    return 'YES' if dp[n] else 'NO'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
