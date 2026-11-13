import sys

def brute(inp):
    a, b = inp.split()[:2]
    best = {}
    for m in range(1 << len(a)):
        key = ''.join(sorted(a[i] for i in range(len(a)) if m >> i & 1))
        best[key] = max(best.get(key, 0), len(key))
    keep = 0
    for m in range(1 << len(b)):
        key = ''.join(sorted(b[i] for i in range(len(b)) if m >> i & 1))
        if key in best:
            keep = max(keep, 2 * len(key))
    return str(len(a) + len(b) - keep)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
