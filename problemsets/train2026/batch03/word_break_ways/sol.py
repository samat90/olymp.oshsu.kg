import sys

def sol(inp):
    a = inp.split()
    s = a[0]
    m = int(a[1])
    ws = set(a[2:2 + m])
    lens = sorted(set(len(w) for w in ws))
    M = 10 ** 9 + 7
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        t = 0
        for L in lens:
            if L > i:
                break
            if s[i - L:i] in ws:
                t += dp[i - L]
        dp[i] = t % M
    return str(dp[n])


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
