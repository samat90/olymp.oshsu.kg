import sys

def sol(inp):
    a, b, c = inp.split()[:3]
    n, m = len(a), len(b)
    if n + m != len(c):
        return 'NO'
    dp = [False] * (m + 1)
    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 and j == 0:
                dp[j] = True
                continue
            v = False
            if i and dp[j] and a[i - 1] == c[i + j - 1]:
                v = True
            if j and dp[j - 1] and b[j - 1] == c[i + j - 1]:
                v = True
            dp[j] = v
    return 'YES' if dp[m] else 'NO'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
