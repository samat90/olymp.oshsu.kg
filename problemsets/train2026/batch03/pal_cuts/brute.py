import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    best = n
    for m in range(1 << (n - 1)):
        parts = []
        st = 0
        for i in range(n - 1):
            if m >> i & 1:
                parts.append(s[st:i + 1])
                st = i + 1
        parts.append(s[st:])
        if all(p == p[::-1] for p in parts):
            best = min(best, len(parts) - 1)
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
