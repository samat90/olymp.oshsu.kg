import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    best = n
    for r in range(n):
        t = s[r:] + s[:r]
        a = sum(1 for i in range(n) if int(t[i]) != i % 2)
        best = min(best, a, n - a)
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
