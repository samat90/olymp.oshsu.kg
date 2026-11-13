import sys

def brute(inp):
    a, b = inp.split()[:2]
    subs = {}
    for m in range(1 << len(a)):
        t = ''.join(a[i] for i in range(len(a)) if m >> i & 1)
        subs[t] = sum(map(ord, t))
    best = 0
    for m in range(1 << len(b)):
        t = ''.join(b[i] for i in range(len(b)) if m >> i & 1)
        if t in subs:
            best = max(best, subs[t])
    return str(sum(map(ord, a)) + sum(map(ord, b)) - 2 * best)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
