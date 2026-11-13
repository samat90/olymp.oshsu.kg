import sys

def sol(inp):
    s = inp.split()[0]
    M = 10 ** 9 + 7
    n = len(s)
    dp = [0] * (n + 2)
    dp[0] = 1
    for c in s:
        nd = [0] * (n + 2)
        for b in range(n + 1):
            v = dp[b]
            if not v:
                continue
            if c in '(?':
                nd[b + 1] = (nd[b + 1] + v) % M
            if c in ')?' and b:
                nd[b - 1] = (nd[b - 1] + v) % M
        dp = nd
    return str(dp[0] % M)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
