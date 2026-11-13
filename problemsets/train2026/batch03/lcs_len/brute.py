import sys

def brute(inp):
    a, b = inp.split()[:2]
    best = 0
    subs = set()
    for m in range(1 << len(a)):
        subs.add(''.join(a[i] for i in range(len(a)) if m >> i & 1))
    for m in range(1 << len(b)):
        t = ''.join(b[i] for i in range(len(b)) if m >> i & 1)
        if t in subs:
            best = max(best, len(t))
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
