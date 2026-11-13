import sys

def sol(inp):
    s = inp.split()[0]
    r = s[::-1]
    n = len(s)
    prev = [0] * (n + 1)
    for i in range(1, n + 1):
        cur = [0] * (n + 1)
        a = s[i - 1]
        for j in range(1, n + 1):
            if a == r[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur
    return str(n - prev[n])


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
