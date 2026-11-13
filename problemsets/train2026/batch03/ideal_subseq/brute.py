import sys

def brute(inp):
    a = inp.split()
    k = int(a[0])
    s = a[1]
    n = len(s)
    best = 0
    for m in range(1, 1 << n):
        t = [ord(s[i]) for i in range(n) if m >> i & 1]
        if all(abs(t[i] - t[i + 1]) <= k for i in range(len(t) - 1)):
            best = max(best, len(t))
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
