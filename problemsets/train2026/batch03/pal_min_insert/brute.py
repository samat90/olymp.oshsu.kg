import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    best = 0
    for m in range(1 << n):
        t = [s[i] for i in range(n) if m >> i & 1]
        if t == t[::-1] and len(t) > best:
            best = len(t)
    return str(n - best)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
